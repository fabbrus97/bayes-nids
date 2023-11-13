using System.Collections.Immutable;
using System.ComponentModel;
using System.Numerics;
using System.Reflection.Emit;
using Microsoft.ML.Probabilistic.Collections;
using Microsoft.ML.Probabilistic.Learners.Mappings;

public class EvaluatorMapping:
    IClassifierEvaluatorMapping<List<Instance>, int, List<string>, bool>
{
    public IEnumerable<int> GetInstances(List<Instance> instanceSource)
    {
        return Enumerable.Range(0, instanceSource.Count());
    }
    public IEnumerable<bool> GetClassLabels(List<Instance> instanceSource, List<string> labelSource)
    {
        var labels = new List<bool>();
        labels.Add(true);
        labels.Add(false);
        return labels;
    }
    public bool GetLabel(int instance, List<Instance> instanceSource, List<string> labelSource)
    {
        return instanceSource[instance].label == "normal";
    }
}
