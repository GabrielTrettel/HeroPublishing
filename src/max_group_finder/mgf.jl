using Distributed
n_of_workers_available = parse(Int64, ARGS[1])
addprocs(n_of_workers_available)

@everywhere import Base.Iterators.partition
@everywhere include("walker.jl")
@everywhere using .MaxGrpFinder
@everywhere using ProgressMeter

function runner()
    n_of_workers_available = parse(Int64, ARGS[1])
    in_folder = ARGS[2]
    out_folder = ARGS[3]

    files = readdir(in_folder)
    chunk_size = Int64(ceil(length(files) / n_of_workers_available))

    println(n_of_workers_available)


    iter = 0
    total = length(files)

    p = Progress(total, barlen=20)

    channel = RemoteChannel(()->Channel{Bool}(total), 1)

    @async while take!(channel)
        ProgressMeter.next!(p; showvalues = [(:iter,iter), (:total,total)])
        iter+=1
    end

    functions = [consummer for _ in 1:n_of_workers_available]
    chunk_for_each_worker  = map(x->[in_folder, out_folder, channel, x], collect(partition(files, chunk_size)))


    pmap((fun,input)->fun(input...), functions, chunk_for_each_worker)
    put!(channel, false)

end

runner()
