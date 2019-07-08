using Distributed
using Combinatorics

module MaxGrpFinder

using Distributed
using Combinatorics
using ProgressMeter


export producer!,
       consummer!

mutable struct Publication
    year     :: Int64
    authors :: Set
end


mutable struct Author
    cnpq         :: String
    publications :: AbstractArray{Publication}
    groups       :: Array
end

norm(x) = lowercase(string(strip(x)))


function producer!(ch::Channel, done::Channel)
    folder = "/home/trettel/Documents/projects/HeroPublishing/src/max_group_finder/publications/"
    all_files = readdir(folder)

    for file in all_files
        name_to_number = Dict{String, Int64}()
        a_index = 0
        publications::AbstractArray = []
        groups = Set()

        for line in readlines(folder*file)
            au = Set()
            yr, authors, _ = map(norm, split(line, " #@# "))
            authors = Set(map(norm, split(authors, ';')))
            new_authors = Set()

            for a in authors
                if a in keys(name_to_number)
                    push!(new_authors, name_to_number[a])
                else
                    push!(name_to_number, a=>a_index)
                    a_index += 1
                    push!(new_authors, name_to_number[a])
                end
            end

            try
                yr = parse(Int64, yr)
            catch
                continue
            end
            # println(new_authors)
            union!(groups, new_authors)
            push!(publications, Publication(yr, new_authors))
        end

        put!(ch, Author(file, publications, collect(groups)))
    end
    put!(ch, "Q")
    put!(done, 1)
end

function pertinency(seta, setb)
    for a in seta
        if !(a in setb) return false end
    end
    return true
end


function qtd(n, dic)
    i = 0
    for v in values(dic)
        if n == v i+=1 end
    end
    return i

end



function walk(author)
    walk = "n_combinations\tbiggest_walk\tn_of_groups_in_tbiggest_walk\n"
    print("\nParsing $(author.cnpq) having $(length(author.groups)) coauthors and $(length(author.publications)) publ \n")
    for n in 1:9
        biggest_walk = 0

        frequecy = Dict()
        total = binomial(length(author.groups), n)
        println("\n\nTotal of combinations = $total")

        prog =  Progress(total, desc="Combinations veryfied n=$n: ",
                        barglyphs=BarGlyphs('|','█', ['▁' ,'▂' ,'▃' ,'▄' ,'▅' ,'▆', '▇'],' ','|',),
                        barlen=10)
        x = 0
        for group in combinations(author.groups, n)
            x+=1
            ProgressMeter.next!(prog; showvalues = [(:x,x)])

            push!(frequecy, group => 0)
            last_yr = 0

            @simd for publication in author.publications
                if pertinency(Set(group), publication.authors) && publication.year > last_yr
                    last_yr = publication.year
                    frequecy[group] += 1
                end
            end
            if frequecy[group] > biggest_walk
                biggest_walk = frequecy[group]
            end
        end
        ProgressMeter.finish!(prog)

        qtd_in_bgst_walk = qtd(biggest_walk, frequecy)
        walk *= "$n\t$biggest_walk\t$qtd_in_bgst_walk\n"
    end

    return walk
end


function consummer!(ch::Channel, done::Channel)
    folder = "/home/trettel/Documents/projects/HeroPublishing/src/max_group_finder/caminhar/"

    for author in ch
        if author == "Q" break end
        # println(author.groups, "\n================================\n")
        steps = walk(author)

        io = open(folder*author.cnpq, "w")
        write(io, steps)
        close(io)

    end
    put!(done, 1)
end

end #module

using .MaxGrpFinder

function runner()
    nworkers = 3
    conductor = Channel(300)
    done = Channel(nworkers)

    @async producer!(conductor, done)
    @async consummer!(conductor, done)

    # for i in 1:nworkers
    #     # @async fetch(j)
    # end

    # @async fetch(p)
    # fetch(p)
    for i=1:nworkers+1 take!(done) end
end

runner()
