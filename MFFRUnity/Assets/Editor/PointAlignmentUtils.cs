using System;
using System.Collections.Generic;
using UnityEngine;

public static class PointAlignmentUtils
{
    public static (Vector2[] adjustedPoints, int firstAlignedIndex) AlignPointsLeftOfP1(Vector2[] points, Vector2 p1)
    {
        if (points == null || points.Length < 2) return (points, -1);

        Vector2[] adjustedPoints = (Vector2[])points.Clone();

        // ① p1から上に伸びる線分との交点を探す（p1自身除く）
        Vector2? intersection = null;

        for (int i = 0; i < points.Length; i++)
        {
            Vector2 a = points[i];
            Vector2 b = points[(i + 1) % points.Length];

            // p1自身の線分と一致しないように確認
            if ((a == p1 || b == p1)) continue;

            // 垂直線との交差をチェック
            if (LineSegmentsIntersect(a, b, p1, p1 + Vector2.up * 1000f, out Vector2 ip))
            {
                intersection = ip;
                break;  // 最初に見つかった交点でOK
            }
        }

        if (!intersection.HasValue)
        {
            Debug.LogWarning("交点が見つかりませんでした。整列は行われません。");
            return (adjustedPoints, -1);
        }

        float cutoffX = Mathf.Min(p1.x, intersection.Value.x);
        int firstAlignedIndex = -1;
        // ② cutoffX より左側にある点の x を p1.x に揃える
        for (int i = 0; i < adjustedPoints.Length; i++)
        {
            if (adjustedPoints[i].x < cutoffX)
            {
                adjustedPoints[i] = new Vector2(p1.x, adjustedPoints[i].y);
            }
            else
            {
                firstAlignedIndex = i;
            }
        }

        return (adjustedPoints, firstAlignedIndex+1);
    }

    private static bool LineSegmentsIntersect(Vector2 p1, Vector2 p2, Vector2 q1, Vector2 q2, out Vector2 intersection)
    {
        intersection = Vector2.zero;
        Vector2 r = p2 - p1;
        Vector2 s = q2 - q1;
        float rxs = r.x * s.y - r.y * s.x;
        float qpxr = (q1 - p1).x * r.y - (q1 - p1).y * r.x;

        if (Mathf.Approximately(rxs, 0f)) return false;

        float t = ((q1 - p1).x * s.y - (q1 - p1).y * s.x) / rxs;
        float u = ((q1 - p1).x * r.y - (q1 - p1).y * r.x) / rxs;

        if (t >= 0f && t <= 1f && u >= 0f && u <= 1f)
        {
            intersection = p1 + t * r;
            return true;
        }

        return false;
    }
}
