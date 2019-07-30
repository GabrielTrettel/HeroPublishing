module PublicationOrg


using Combinatorics
using ProgressMeter

export Publication,
       Author,
       Authors

mutable struct Publication
    year     :: Int64
    authors :: Set
end


mutable struct Author
    cnpq         :: String
    publications :: Array{Publication}
    unique_authors :: Array
    groups :: Dict
    n_max_coauth :: Int64
end


mutable struct Authors
    folder :: String
    file_list :: Array{String}
    function Authors(infolder)
        fl = readdir(infolder)
        new(infolder, fl)
    end
end


norm(x) = lowercase(string(strip(x)))

function Base.iterate(authors::Authors, state=1)
    if length(authors.file_list) <= 0 return (nothing) end

    file = pop!(authors.file_list)
    folder = authors.folder


    name_to_number = Dict{String, Int64}()
    a_index = 0
    publications::AbstractArray = []
    unique_authors = Set()
    max_authors = 0

    for line in readlines(folder*file)
        au = Set()
        yr, authors, _ = map(norm, split(line, " #@# "))
        authors = Set(map(norm, split(authors, ';')))
        # new_authors = authors
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

        union!(unique_authors, new_authors)
        push!(publications, Publication(yr, new_authors))
    end

    author = Author(file, publications, collect(unique_authors), Dict(), max_authors)
    author.groups = groups_by_n(author)


    return (author, state+1)
end



function groups_by_n(author::Author)
    publications = author.publications
    groups = Dict()

    for qtd_aut in 1:9
        authors_in_common = filter(x-> length(x.authors) >= qtd_aut, publications)
        authors_in_common = map(x->x.authors, authors_in_common)

        if length(authors_in_common) <= 0 continue end
        qtd_aut_in_common = Set(collect(Iterators.flatten(authors_in_common)))

        push!(groups, qtd_aut=>collect(qtd_aut_in_common))
    end
    return groups
end

# using JSON
function teste()
    l = "/home/trettel/Documents/projects/HeroPublishing/src/max_group_finder/publications/"

    for a in Authors(l)
        fill_groups_by_n!(a)
        println("$(a.cnpq)   -> $(a.n_max_coauth)\n$(a.unique_authors)")
        print(json(a.groups, 4))
        break
    end
end

# teste()

end #module
