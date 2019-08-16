using ProgressMeter
using IterTools


function fetch_walks(walk_folder::String, out_folder::String)
    files = readdir(walk_folder)

    p = Progress(length(files), barlen=20)
    data = Dict([(k , Int64[]) for k in 2:10])

    for file in files
        # @show file
        ProgressMeter.next!(p)
        lines = map(x->split(x, "\t"), readlines("$walk_folder/$file"))[2:end]
        lines = [map(f->parse(Int64,f), line) for line in lines]

        # @show lines
        for (n, bw, _) in lines
            push!(data[n], bw)
        end
    end

    lines = ""
    for (k,v) in sort(collect(data), by=x->x[1])
        numbers = join(v, " ")
        lines *= "$k\t$numbers\n"
    end
    write("$out_folder/$walk_folder.wlk", lines)

    ProgressMeter.finish!(p)
end



function main()
    walk_folder = ARGS[1]
    out_folder  = ARGS[2]

    fetch_walks(walk_folder, out_folder)
end

main()
