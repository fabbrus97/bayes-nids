[Serializable]
public class Instance
{
    public double[] values { get; set;}
    public string label;
    private int[] base_index { get; set; }
    public bool[] isSparse { get; set;}
    //not the count of all the features, but just the one with 
    //values > 0 - since the representation is sparse
    public int featureCount { get; set;}
    public int GetFeatureIndex(int n_feature)
    {   
        //TODO Getting feature 36 is_sm_ips_ports index -> 92913; value: 3 why is_sm_ips... ha valore 3 ?!?
        //this is the bias

        // Console.WriteLine("Features: " + Program.Features.Count() + " base_index: " + base_index.Length + " isSparse: " + isSparse.Length + " featureCount: " + featureCount);

        
        // if (n_feature >= featureCount)
        // {
        //     return base_index[featureCount];//+1;
        // }

        var index = base_index[n_feature];
        
        double val = 1; 
        if(!isSparse[n_feature])
        {
            index += 1;
            val = values[n_feature]; //the sparse features indexes start at 1
        }
        else
        {
            index += (int)values[n_feature];
        }
        
        // if (n_feature == 1) 
            // Console.WriteLine("Getting feature " + n_feature + " " + Program.Features[n_feature] +  " index -> " + index + "; value: " + val);
        // else
        //     Console.WriteLine("Getting feature " + n_feature + " " + "bias" +  " index -> " + index + "; value: " + val);


        return index;
    }
    /*
    values: if the feature is dense, it is an actual value. If the feature is sparse (was one-hot encoded), it is an index (the actual value is 1)
    is_sparse_bitmask: if is_sparse_bitmask[i] is true, then values[i] is an index (and its value is 1), else it is an actual value
    NOTE: the index of a non-sparse feature is always 0
    */
    public Instance(double[] values, int[] base_index, bool[] is_sparse_bitmask, string label)
    {
        this.values = new double[values.Length + 1];
        Array.Copy(values, this.values, values.Length);
        this.values[values.Length] = 1; //this is the bias
       
        this.label = label;
       
        this.base_index = new int[base_index.Length+1]; 
        Array.Copy(base_index, this.base_index, base_index.Length);
        this.base_index[this.base_index.Length - 1] = this.base_index[this.base_index.Length - 2] + 1; //bias index

        // for (int i = 0; i < Program.Features.Count() ; i++)
        // {
        //     Console.WriteLine("Feature: " + Program.Features[i] + " Base Index: " + this.base_index[i]);
        // }
        // Console.WriteLine("Bias: " + this.base_index[this.base_index.Length - 1]);


        this.isSparse = new bool[is_sparse_bitmask.Length+1];
        Array.Copy(is_sparse_bitmask, this.isSparse, is_sparse_bitmask.Length);
        this.isSparse[is_sparse_bitmask.Length] = false; //bias isSparse value
        this.featureCount = values.Count(); //counting bias
        
    }
}