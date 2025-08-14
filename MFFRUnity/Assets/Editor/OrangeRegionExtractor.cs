using UnityEngine;
using System.Collections.Generic;
using System.Linq;

public static class OrangeRegionExtractor
{
    public static Vector2[] Extract(Vector2[] points, Vector2[] orangeLine)
    {
        List<Vector2> result = new List<Vector2>();
        Vector2? firstIntersection = null;
        Vector2? lastIntersection = null;

        for (int i = 0; i < points.Length - 1; i++)
        {
            Vector2 pt = points[i];
            Vector2 next = points[i + 1];

            float y0 = GetOrangeYAtX(pt.x, orangeLine, out bool valid0);
            float y1 = GetOrangeYAtX(next.x, orangeLine, out bool valid1);
            bool above0 = valid0 && pt.y > y0;
            bool above1 = valid1 && next.y > y1;

            // 上昇して交差
            if (!above0 && above1)
            {
                Vector2 inter = Vector2.Lerp(pt, next, GetSegmentInterpolationT(pt, next, orangeLine));
                firstIntersection ??= inter;
                result.Add(inter);
                result.Add(next);
            }
            // 上に残る
            else if (above0 && above1)
            {
                result.Add(next);
            }
            // 降下して交差
            else if (above0 && !above1)
            {
                Vector2 inter = Vector2.Lerp(pt, next, GetSegmentInterpolationT(pt, next, orangeLine));
                result.Add(inter);
                lastIntersection = inter;
            }
        }

        // 必ず両端に交点が来るように修正
        if (firstIntersection.HasValue && lastIntersection.HasValue)
        {
            // 開始位置をfirstIntersectionにそろえるようにローテート
            int startIdx = result.FindIndex(p => ApproximatelyEqual(p, firstIntersection.Value));
            int endIdx = result.FindLastIndex(p => ApproximatelyEqual(p, lastIntersection.Value));

            if (startIdx >= 0 && endIdx >= 0 && endIdx > startIdx)
            {
                result = result.GetRange(startIdx, endIdx - startIdx + 1);
            }
            else
            {
                // 順序が壊れてる場合：回転して整える
                var rotated = new List<Vector2>();
                for (int i = 0; i < result.Count; i++)
                    rotated.Add(result[(startIdx + i) % result.Count]);

                result = rotated;
                // 末尾に lastIntersection を追加（重複防止）
                if (!ApproximatelyEqual(result.Last(), lastIntersection.Value))
                    result.Add(lastIntersection.Value);
            }
        }

        return result.ToArray();
    }

    private static bool ApproximatelyEqual(Vector2 a, Vector2 b, float epsilon = 1e-4f)
    {
        return (a - b).sqrMagnitude < epsilon * epsilon;
    }

    private static float GetOrangeYAtX(float x, Vector2[] orange, out bool valid)
    {
        valid = false;
        for (int i = 0; i < orange.Length - 1; i++)
        {
            float x0 = orange[i].x, x1 = orange[i + 1].x;
            if ((x >= Mathf.Min(x0, x1)) && (x <= Mathf.Max(x0, x1)))
            {
                valid = true;
                float t = (x - x0) / (x1 - x0);
                return Mathf.Lerp(orange[i].y, orange[i + 1].y, t);
            }
        }
        return 0f;
    }

    private static float GetSegmentInterpolationT(Vector2 a, Vector2 b, Vector2[] orange)
    {
        float xMid = (a.x + b.x) * 0.5f;
        float yOrange = GetOrangeYAtX(xMid, orange, out _);
        return Mathf.Approximately(b.y, a.y) ? 0.5f : (yOrange - a.y) / (b.y - a.y);
    }
}
