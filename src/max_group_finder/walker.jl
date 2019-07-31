module MaxGrpFinder

using Distributed
using Combinatorics
using ProgressMeter

export consummer

include("fetch_publications.jl")
using .PublicationOrg

function verify_comb(author::Author, n::Integer)

    biggest_walk = 0
    n_of_biggest_walks = 0
    total = (binomial(length(author.groups[n]),n))

    # prog =  Progress(total, desc="\t\33[37m p=$(length(author.groups[n])) n=$n \t comb=$total\t",
    #                 barglyphs=BarGlyphs('|','█', ['▁' ,'▂' ,'▃' ,'▄' ,'▅' ,'▆', '▇'],' ','|',),
    #                 barlen=10)

    for group in combinations(author.groups[n], n)
        # ProgressMeter.next!(prog)
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
    # ProgressMeter.finish!(prog)

    return biggest_walk, n_of_biggest_walks
end


function walk(author::Author)
    walk_txt = "n_combinations\tbiggest_walk\tn_of_groups_in_tbiggest_walk\n"
    # println("\t\33[37m Parsing $(author.cnpq)")
    for n in 1:9
        biggest_walk, n_of_biggest_walks = (0,0)

        if haskey(author.groups, n)
            total = (binomial(length(author.groups[n]),n))
            if total >= 51_971_283 # This ammount takes about 20 minutes to run, so NFW
                # println("\t\33[37m p=$(length(author.groups[n])) n=$n \t comb=$total\t")
                return nothing
            end

            biggest_walk, n_of_biggest_walks = verify_comb(author, n)
        end

        walk_txt *= "$(n+1)\t$biggest_walk\t$n_of_biggest_walks\n"
    end

    # println("\t\33[37m Done here")
    return walk_txt
end


function consummer(in_folder::String, out_folder::String, ch::RemoteChannel, files_to_parse=nothing)
    # folder = "/home/trettel/Documents/projects/HeroPublishing/src/max_group_finder/caminhar/"
    authors = Authors(in_folder, files_to_parse)

    total = length(authors.file_list)
    to_hard_to_parse = ""
    already_parsed = 0

    for author in authors
        already_parsed+=1
        # println("\33[35m Parsing $already_parsed/$total")
        put!(ch, true)
        steps = walk(author)
        if steps == nothing
            # println("\t\33[31m Too hard to parse, sorry...")
            to_hard_to_parse *= author.cnpq * "\n"
            continue
        end

        io = open(out_folder*author.cnpq, "w")
        write(io, steps); close(io)
    end

    if length(to_hard_to_parse) > 0
        i = 0
        file_name = "to_hard_to_parse"*string(i)
        while isfile(file_name)
            i+=1
            file_name = filename[1:end-1]*string(i)
        end
        file_name*=".list"
        io = open(file_name)
        write(io, to_hard_to_parse); close(io)
    end
end

end #module
