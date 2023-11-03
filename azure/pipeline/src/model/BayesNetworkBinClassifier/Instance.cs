public class Instance
{
    public double[] values { get; set;}
    public string label;
    private int[] base_index { get; set; }
    public bool[] isSparse { get; set;}
    public int featureCount { get; set;}
    public int GetFeatureIndex(int n_feature)
    {
        var index = base_index[n_feature];

        if(!isSparse[n_feature])
            index += 1;
        else
            index += (int)values[n_feature];
        
        
        return index;
    }
    /*
    values: if the feature is dense, it is an actual value. If the feature is sparse (was one-hot encoded), it is an index (the actual value is 1)
    is_sparse_bitmask: if is_sparse_bitmask[i] is true, then values[i] is an index (and its value is 1), else it is an actual value
    NOTE: the index of a non-sparse feature is always 0
    */
    public Instance(double[] values, int[] base_index, bool[] is_sparse_bitmask, string label)
    {
        this.values = values;
        this.label = label;
        this.base_index = base_index;
        this.isSparse = is_sparse_bitmask;
        this.featureCount = values.Count();
        
    }
}