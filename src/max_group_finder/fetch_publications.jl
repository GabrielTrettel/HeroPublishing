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
    publications :: AbstractArray{Publication}
    unique_authors :: Array
    groups       :: Array{Array}
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
    if length(authors.file_list) <= 0 || state==10 return (nothing) end

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

    return (Author(file, publications, collect(unique_authors), max_authors), state+1)
end


function teste()
    l = "/home/trettel/Documents/projects/HeroPublishing/src/max_group_finder/publications/"

    for a in Authors(l)
        println(a.cnpq)
    end
end

# teste()

end #module
