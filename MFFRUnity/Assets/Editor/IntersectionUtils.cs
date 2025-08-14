using UnityEngine;
using System.Collections.Generic;
using System.Linq;

public static class IntersectionUtils
{
    public static Vector2[] GetLineIntersections(Vector2[] poly, Vector2 lineStart, Vector2 lineEnd)
    {
        List<Vector2> hits = new List<Vector2>();
        for (int i = 0; i < poly.Length; i++)
        {
            Vector2 p1 = poly[i];
            Vector2 p2 = poly[(i + 1) % poly.Length];
            if (IntersectSegments(p1, p2, lineStart, lineEnd, out Vector2 ip))
                hits.Add(ip);
        }
        return hits.ToArray();
    }

    public static Vector2? GetClosestIntersection(Vector2[] poly, Vector2 start, Vector2 end, float targetX)
    {
        var hits = GetLineIntersections(poly, start, end);
        return hits.OrderBy(p => Mathf.Abs(p.x - targetX)).FirstOrDefault();
    }

    public static bool IntersectSegments(Vector2 p1, Vector2 p2, Vector2 q1, Vector2 q2, out Vector2 ip)
    {
        ip = Vector2.zero;
        Vector2 r = p2 - p1;
        Vector2 s = q2 - q1;
        float rxs = r.x * s.y - r.y * s.x;
        if (Mathf.Approximately(rxs, 0f)) return false;

        float t = ((q1 - p1).x * s.y - (q1 - p1).y * s.x) / rxs;
        float u = ((q1 - p1).x * r.y - (q1 - p1).y * r.x) / rxs;
        if (t >= 0f && t <= 1f && u >= 0f && u <= 1f)
        {
            ip = p1 + t * r;
            return true;
        }
        return false;
    }
}
