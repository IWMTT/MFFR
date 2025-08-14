// GraphNode.cs
using UnityEditor;
using UnityEngine;
using System.Collections.Generic;
using System.Linq;

public class TorusSectionController : MonoBehaviour
{
    [SerializeField, Range(1, 50)]
    private int segmentation = 18;
    
    // [SerializeField, Range(20, 2000),HideInInspector]
    // private int resolution = 1000;

    [SerializeField] private float R = 6.2f;
    [SerializeField] private float a = 2.0f;
    [SerializeField] private float kappa = 1.7f;
    [SerializeField] private float delta = 0.33f;
    [SerializeField] private float innerHeight = -2.4f;
    [SerializeField] private float outerHeight = -3.1f;

    [SerializeField] private float thickness = 0.5f;
    [SerializeField] private bool identicalInboard = true;
    public ExternalTool externalTool;





    private int pointCount = 1000; //=> resolution ;
    public int PointCount => pointCount;
    public int Segmentation => segmentation;
    public float R_major => R;
    public float A_minor => a;
    public float Kappa => kappa;
    public float Delta => delta;
    public float InnerHeight => innerHeight;
    public float OuterHeight => outerHeight;
    public float Thickness => -thickness;
    public bool IdenticalInboard => identicalInboard;



    private void OnValidate()
    {
        // pointCount = Mathf.Max(3, resolution * 2);
        var btc = GetComponent<BlanketToroidalDivisionController>();
        if (btc != null)
        {
            // 値を連動させる
            btc.PoloidalSegmentation = segmentation;
            btc.ChangeBlanketCoordinatesLength(segmentation);
            btc.OnValidate();
        }
    }



    /// <summary>
    /// 近似D型断面に基づく点列を取得（2D）
    /// </summary>
    public Vector2[] GetApproximatedPoints(float offset = 0f)
    {
        Vector2[] points = new Vector2[pointCount];
        for (int i = 0; i < pointCount; i++)
        {
            float theta = Mathf.PI * 2f * i / pointCount;
            float r = (a + offset) * (1 + delta * Mathf.Cos(theta));
            float x = R + r * Mathf.Cos(theta);
            float z = (a + offset) * kappa * Mathf.Sin(theta);
            points[i] = new Vector2(x, z); // X-Z 平面上に
        }
        return points;
    }

    /// <summary>
    /// 指定したY座標のラインと交差するインデックス範囲（始点・終点）を取得
    /// </summary>
    public (int startIndex, int endIndex)? GetDiverterRange(float yInner, float yOuter)
    {
        Vector2[] inner = GetApproximatedPoints();
        int n = inner.Length;
        List<int> inside = new();

        for (int i = 0; i < n; i++)
        {
            float y = inner[i].y;
            if (y >= yInner && y <= yOuter)
                inside.Add(i);
        }

        if (inside.Count < 2)
            return null;

        int minIndex = inside[0];
        int maxIndex = inside[inside.Count - 1];
        return (minIndex, maxIndex);
    }

    /// <summary>
    /// 指定インデックス範囲を segmentation + 1 に分割
    /// </summary>
    public int[] GetSegmentDivisions(int startIndex, int endIndex)
    {
        int[] result = new int[segmentation + 1];
        int len = endIndex - startIndex + 1;

        for (int i = 0; i <= segmentation; i++)
        {
            float t = (float)i / segmentation;
            int idx = startIndex + Mathf.RoundToInt(t * len);
            result[i] = Mathf.Clamp(idx, 0, PointCount - 1);
        }
        return result;
    }
    public Vector2[] GetOffsetPoints(Vector2[] basePoints, float offset)
    {
        int count = basePoints.Length;
        Vector2[] offsetPoints = new Vector2[count];

        for (int i = 0; i < count; i++)
        {
            Vector2 p0 = basePoints[(i - 1 + count) % count];
            Vector2 p1 = basePoints[i];
            Vector2 p2 = basePoints[(i + 1) % count];

            Vector2 dir = ((p2 - p1).normalized + (p1 - p0).normalized).normalized;
            Vector2 normal = new Vector2(-dir.y, dir.x).normalized;
            offsetPoints[i] = p1 + normal * offset;
        }

        return offsetPoints;
    }

    
}
