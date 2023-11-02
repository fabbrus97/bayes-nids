public class Instance
{
    public double[] values {get; set;}
    public string label;
    public bool[] isSparse {get; set;}
    public int featureCount {get; set;}

    /*
    values: if the feature is dense, it is an actual value. If the feature is sparse (was one-hot encoded), it is an index (the actual value is 1)
    is_sparse_bitmask: if is_sparse_bitmask[i] is true, then values[i] is an index (and its value is 1), else it is an actual value
    NOTE: the index of a non-sparse feature is always 0
    */
    public Instance(double[] values, bool[] is_sparse_bitmask, string label)
    {
        this.values = values;
        this.label = label;
        this.isSparse = is_sparse_bitmask;
        this.featureCount = values.Count();
        
    }
}