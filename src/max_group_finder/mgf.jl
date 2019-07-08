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
    n_max_coauth :: Int64
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
        max_authors = 0
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
            if length(new_authors) > max_authors
                max_authors = length(new_authors)
            end

            union!(groups, new_authors)
            push!(publications, Publication(yr, new_authors))
        end

        put!(ch, Author(file, publications, collect(groups), max_authors))
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


function verify_comb(author, n)
    biggest_walk = 0
    n_of_biggest_walks = 0

    total = binomial(length(author.groups), n)
    println("\n\nTotal of combinations = $total")

    prog =  Progress(total, desc="Combinations veryfied n=$(n+1): ",
                    barglyphs=BarGlyphs('|','█', ['▁' ,'▂' ,'▃' ,'▄' ,'▅' ,'▆', '▇'],' ','|',),
                    barlen=10)
    x = 0
    for group in combinations(author.groups, n)
        ProgressMeter.next!(prog; showvalues = [(:x,x)])
        x+=1
        walk = 0
        last_yr = 0

        for publication in author.publications
            if Set(group) == publication.authors && publication.year > last_yr
                last_yr = publication.year
                walk += 1
            end
        end
        if walk > biggest_walk
            biggest_walk = walk
            n_of_biggest_walks = 1
        elseif walk == biggest_walk && walk != 0
            n_of_biggest_walks += 1
        end
    end
    ProgressMeter.finish!(prog)
    return biggest_walk, n_of_biggest_walks
end


function walk(author)
    walk_txt = "n_combinations\tbiggest_walk\tn_of_groups_in_tbiggest_walk\n"
    print("\nParsing $(author.cnpq) having $(length(author.groups)) coauthors and $(length(author.publications)) publ \n")
    for n in 1:9
        biggest_walk, n_of_biggest_walks = (0,0)
        if n <= author.n_max_coauth
            biggest_walk, n_of_biggest_walks = verify_comb(author, n)
        end

        walk_txt *= "$(n+1)\t$biggest_walk\t$n_of_biggest_walks\n"
    end

    return walk_txt
end


function consummer!(ch::Channel, done::Channel)
    folder = "/home/trettel/Documents/projects/HeroPublishing/src/max_group_finder/caminhar/"

    for author in ch
        if author == "Q" break end
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
    consummer!(conductor, done)

    # for i=1:1 take!(done) end
end

runner()
