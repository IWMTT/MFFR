using UnityEngine;
using System.Collections.Generic;

public static class SegmentedPolyline
{
    public static Vector2[] DivideByLength(Vector2[] polyline, int segments)
    {
        float totalLength = 0f;
        float[] lengths = new float[polyline.Length - 1];

        for (int i = 0; i < lengths.Length; i++)
        {
            lengths[i] = Vector2.Distance(polyline[i], polyline[i + 1]);
            totalLength += lengths[i];
        }

        List<Vector2> result = new List<Vector2>();
        result.Add(polyline[0]);

        float step = totalLength / segments;
        float currentDist = step;
        int segIndex = 0;

        for (int i = 1; i < segments; i++)
        {
            while (segIndex < lengths.Length && currentDist > lengths[segIndex])
            {
                currentDist -= lengths[segIndex];
                segIndex++;
            }

            if (segIndex < lengths.Length)
            {
                float t = currentDist / lengths[segIndex];
                Vector2 p = Vector2.Lerp(polyline[segIndex], polyline[segIndex + 1], t);
                result.Add(p);
                currentDist = step;
            }
        }

        result.Add(polyline[polyline.Length - 1]);
        return result.ToArray();
    }
}
