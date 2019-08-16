using Distributed

n_of_workers_available = parse(Int64, ARGS[1])
addprocs(n_of_workers_available)
n_of_workers_available-=1

@everywhere import Base.Iterators.partition
@everywhere include("walker.jl")
@everywhere using .MaxGrpFinder
@everywhere using ProgressMeter

function runner()
    n_of_workers_available = parse(Int64, ARGS[1])
    in_folder = ARGS[2]
    out_folder = ARGS[3]

    files = intersect(Set(readdir(in_folder)), Set(map(x->string(strip(x)), readlines(ARGS[4]))))
    setdiff!(files, Set(readdir(out_folder)))
    files = collect(files)

    @show chunk_size = ceil(length(files) / n_of_workers_available) |> Int64

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


    pmap((fun,inputs)->fun(inputs...), functions, chunk_for_each_worker)
    put!(channel, false)

end

@time runner()

setdiff!(Set([1,2,3,4]), Set([1,2,6,7]))
