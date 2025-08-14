using UnityEngine;
using System.Collections.Generic;

public class TorusSectionGenerator
{
    private float R, A, Kappa, Delta;

    public TorusSectionGenerator(float R, float A, float Kappa, float Delta)
    {
        this.R = R;
        this.A = A;
        this.Kappa = Kappa;
        this.Delta = Delta;
    }

    public Vector2[] Generate(int pointCount)
    {
        Vector2[] points = new Vector2[pointCount];
        for (int i = 0; i < pointCount; i++)
        {
            float theta = 2f * Mathf.PI * i / pointCount;
            float r = A * (1 + Delta * Mathf.Cos(theta));
            float x = R + r * Mathf.Cos(theta);
            float y = A * Kappa * Mathf.Sin(theta);
            points[i] = new Vector2(x, y);
        }
        return points;
    }

    public Vector2[] ClipAboveHeights(Vector2[] poly, float yMin, float yMax)
    {
        List<Vector2> result = new List<Vector2>();
        for (int i = 0; i < poly.Length; i++)
        {
            Vector2 p1 = poly[i];
            Vector2 p2 = poly[(i + 1) % poly.Length];

            bool above1 = (p1.y >= yMin && p1.y <= yMax);
            bool above2 = (p2.y >= yMin && p2.y <= yMax);

            if (above1) result.Add(p1);

            // 高さをまたぐ場合は交点を計算
            if (above1 != above2)
            {
                float t = Mathf.InverseLerp(p1.y, p2.y, Mathf.Clamp(p2.y, yMin, yMax));
                Vector2 intersection = Vector2.Lerp(p1, p2, t);
                result.Add(intersection);
            }
        }
        return result.ToArray();
    }
}
