public class SparseFeatureIndex
{
    public Dictionary<string, int> Features { get; set; }
}

public class Feature 
{
    public string name { get; set; }
    public int maxVal { get; set; }
}