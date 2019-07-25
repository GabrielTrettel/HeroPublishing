module MaxGrpFinder

# using Distributed
using Combinatorics
using ProgressMeter


export consummer!



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

    for group in combinations(author.groups[n], n)
        walk = 0
        last_yr = 0

        grp = Set(group)
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
    return biggest_walk, n_of_biggest_walks
end


function walk(author)
    walk_txt = "n_combinations\tbiggest_walk\tn_of_groups_in_tbiggest_walk\n"
    # print("\nParsing $(author.cnpq) having $(length(author.groups)) coauthors and $(length(author.publications)) publ \n")
    for n in 1:9
        biggest_walk, n_of_biggest_walks = (0,0)
        if n <= author.n_max_coauth
            biggest_walk, n_of_biggest_walks = verify_comb(author, n)
        end

        walk_txt *= "$(n+1)\t$biggest_walk\t$n_of_biggest_walks\n"
    end

    return walk_txt
end


function consummer!(authors, in_folder, out_folder)
    # folder = "/home/trettel/Documents/projects/HeroPublishing/src/max_group_finder/caminhar/"
    authors = authors(in_folder)

    total = length(authors.file_list)

    prog =  Progress(total, desc="Authors to parse $total: ",
                    barglyphs=BarGlyphs('|','█', ['▁' ,'▂' ,'▃' ,'▄' ,'▅' ,'▆', '▇'],' ','|',),
                    barlen=10)

    already_parsed = 0
    for author in authors
        already_parsed+=1
        ProgressMeter.next!(prog; showvalues = [(:already_parsed,already_parsed)])

        steps = walk(author)

        io = open(out_folder*author.cnpq, "w")
        write(io, steps)
        close(io)
    end
    ProgressMeter.finish!(prog)
end

end #module


include("fetch_publications.jl")
using .MaxGrpFinder
using .PublicationOrg

function runner()

    in_folder = ARGS[1]
    out_folder = ARGS[2]

    consummer!(Authors, in_folder, out_folder)

    # for i=1:1 take!(done) end
end

runner()
