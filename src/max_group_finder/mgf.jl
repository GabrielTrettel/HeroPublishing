using Distributed


mutable struct Publication
    yar     :: Int64
    authors :: AbstractArray{String}
    title   :: String
end


function producer!( ch::Channel)

end
