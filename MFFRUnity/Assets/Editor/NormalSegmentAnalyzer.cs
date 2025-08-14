using UnityEngine;
using System.Collections.Generic;

public static class NormalSegmentAnalyzer
{
    public static (Vector2[] midpoints, Vector2[] normals) 
        AnalyzeSegmentNormals(Vector2[] clippedRegion, int division, int thres)
    {
        if (clippedRegion == null || clippedRegion.Length < 2 || division <= 0)
            return (new Vector2[0], new Vector2[0]);

        // 線分長と累積長さ
        float totalLength = 0f;
        float[] segmentLengths = new float[clippedRegion.Length - 1];
        for (int i = 0; i < clippedRegion.Length - 1; i++)
        {
            float len = Vector2.Distance(clippedRegion[i], clippedRegion[i + 1]);
            segmentLengths[i] = len;
            totalLength += len;
        }

        // 分割長
        float segmentInterval = totalLength / division;

        // 各区間に含まれるインデックスをまとめる
        List<List<int>> groupedIndices = new List<List<int>>();
        for (int i = 0; i < division; i++) groupedIndices.Add(new List<int>());

        float accumulated = 0f;
        int currentDivision = 0;
        for (int i = 0; i < segmentLengths.Length; i++)
        {
            groupedIndices[currentDivision].Add(i);
            accumulated += segmentLengths[i];
            if (accumulated > (currentDivision + 1) * segmentInterval && currentDivision < division - 1)
            {
                currentDivision++;
            }
        }

        // 各区間の中点と法線を求める
        Vector2[] midpoints = new Vector2[division];
        Vector2[] normals = new Vector2[division];

        for (int i = 0; i < division; i++)
        {
            var indices = groupedIndices[i];
            if (indices.Count == 0)
            {
                midpoints[i] = Vector2.zero;
                normals[i] = Vector2.zero;
                continue;
            }

            // 中点を求める
            List<Vector2> segmentPoints = new List<Vector2>();
            foreach (int idx in indices)
            {
                segmentPoints.Add(clippedRegion[idx]);
                segmentPoints.Add(clippedRegion[idx + 1]);
            }

            Vector2 sum = Vector2.zero;
            foreach (var pt in segmentPoints)
                sum += pt;
            midpoints[i] = sum / segmentPoints.Count;

            // 法線ベクトルの平均
            if (indices.Count > thres)
            {
                // 特別処理：法線は (0,0)-(1,0) の線に垂直 → (0,1)
                normals[i] = new Vector2(0f, 1f);
            }
            else
            {
                Vector2 normalSum = Vector2.zero;
                foreach (int idx in indices)
                {
                    Vector2 edge = clippedRegion[idx + 1] - clippedRegion[idx];
                    Vector2 normal = new Vector2(-edge.y, edge.x).normalized;
                    normalSum += normal;
                }
                normals[i] = normalSum.normalized;
            }
        }

        return (midpoints, normals);
    }
}
