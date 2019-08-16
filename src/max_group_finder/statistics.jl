using Plotly
# using Plots
using ORCA

function build_data_structure(file::String)
    walks = []
    for line in readlines(file)
        n, walk = split(line, "\t")
        walk = map(x->parse(Int64, x), split(walk, " "))
        n = parse(Int64,n)
        push!(walks, walk)
    end
    # return DataFrame(n=2:10, walks=walks)
    return collect(zip(2:10, walks))
end


function my_plot(df, out_file_name)
    # @df _df boxplot!(:n,:walks, alpha=0.75)

    data = GenericTrace[box(y=y,
                            name="$n autores",
                            boxpoints="suspectedoutliers",
                            line_width=1,
                            marker_size=2,
                            boxmean=true) for (n,y) in df]



    layout = Layout(;title="Maior caminhar por autor",
                    xaxis=attr(;showgrid=false, zeroline=false,
                                tickangle=20, showticklabels=true))


    p = Plotly.plot(data, layout)
    savefig(p, out_file_name)
end

function run()
    # folder = ARGS[1]
    # out_folder = ARGS[2]
    folder = "processed_data"
    out_folder = "plots"
    for file in readdir(folder)
        df = build_data_structure("$folder/$file")
        file = file[1:end-4]
        my_plot(df, "$out_folder/$file.pdf")
    end
end
