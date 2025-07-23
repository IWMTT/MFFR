using UnityEngine;

public class GraphNode : MonoBehaviour
{
    [SerializeField, Range(3, 100)]
    private int pointCount = 20;

    [SerializeField] private float R = 6.2f;
    [SerializeField] private float a = 2.0f;
    [SerializeField] private float kappa = 1.7f;
    [SerializeField] private float delta = 0.33f;

    public int PointCount => pointCount;
    public float R_major => R;
    public float A_minor => a;
    public float Kappa => kappa;
    public float Delta => delta;

    /// <summary>
    /// ‹ß—DŒ^’f–Ê‚ÉŠî‚Ã‚­“_—ñ‚ğæ“¾i2Dj
    /// </summary>
    public Vector2[] GetApproximatedPoints()
    {
        Vector2[] points = new Vector2[pointCount];
        for (int i = 0; i < pointCount; i++)
        {
            float theta = Mathf.PI * 2f * i / pointCount;
            float r = a * (1 + delta * Mathf.Cos(theta));
            float x = R + r * Mathf.Cos(theta);
            float z = a * kappa * Mathf.Sin(theta);
            points[i] = new Vector2(x, z); // X-Z •½–Êã‚É
        }
        return points;
    }
}
