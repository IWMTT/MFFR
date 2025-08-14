using UnityEditor;
using UnityEngine;
using System.Linq;
using System.Collections.Generic;

public class GraphEditorView
{
    private Rect rect;
    private Vector2 center;
    private float scale;
    private Vector2 viewCenter;

    public GraphEditorView(Rect rect, float R, float A)
    {
        this.rect = rect;

        // 固定描画範囲
        float minX = 0f;
        float maxX = 2f * R;
        float minY = -3f * A;
        float maxY = 3f * A;

        center = new Vector2((minX + maxX) / 2f, (minY + maxY) / 2f);
        float margin = 1.0f;
        scale = Mathf.Min(rect.width / ((maxX - minX) * margin), rect.height / ((maxY - minY) * margin));
        viewCenter = rect.center;
    }
    public void DrawBackground()
    {
        EditorGUI.DrawRect(rect, new Color(0.1f, 0.1f, 0.1f));
    }

    public Vector2 DataToView(Vector2 p)
    {
        Vector2 rel = p - center;
        rel.y *= -1f;
        return viewCenter + rel * scale;
    }

    public void DrawPolyline(List<Vector2> points, Color color, bool closed = true)
    {
        if (points == null || points.Count < 2) return;

        Handles.color = color;
        for (int i = 0; i < points.Count - 1; i++)
        {
            Handles.DrawLine(DataToView(points[i]), DataToView(points[i + 1]));
        }

        if (closed)
        {
            Handles.DrawLine(DataToView(points[points.Count - 1]), DataToView(points[0]));
        }
    }
    public void DrawAxisWithTicks(float R, float A)
    {
        Handles.color = Color.gray;

        // X軸目盛（0 ~ 2R）
        for (int i = 0; i <= Mathf.CeilToInt(2f * R); i += 1)
        {
            float x = DataToView(new Vector2(i, 0)).x;
            Handles.DrawLine(new Vector2(x, rect.yMin), new Vector2(x, rect.yMax));
            if (i % 5 == 0)
                Handles.Label(new Vector2(x + 2, viewCenter.y + 4), $"{i}m", EditorStyles.miniLabel);
        }

        // Y軸目盛（-3A ~ +3A）
        for (int i = -Mathf.CeilToInt(3f * A); i <= Mathf.CeilToInt(3f * A); i += 1)
        {
            float y = DataToView(new Vector2(0, i)).y;
            Handles.DrawLine(new Vector2(rect.xMin, y), new Vector2(rect.xMax, y));
            if (i % 5 == 0)
                Handles.Label(new Vector2(viewCenter.x + 5, y - 8), $"{i}m", EditorStyles.miniLabel);
        }

        Handles.color = Color.white;
        Handles.DrawLine(new Vector2(rect.xMin, viewCenter.y), new Vector2(rect.xMax, viewCenter.y)); // X軸
        Handles.DrawLine(new Vector2(viewCenter.x, rect.yMin), new Vector2(viewCenter.x, rect.yMax)); // Y軸
    }

    public void DrawNormals(Vector2[] midpoints, Vector2[] normals, float length = 0.5f)
    {
        if (midpoints.Length != normals.Length) return;

        Handles.color = Color.green;

        for (int i = 0; i < midpoints.Length; i++)
        {
            Vector2 start = DataToView(midpoints[i]);
            Vector2 end = DataToView(midpoints[i] + normals[i] * length);
            Handles.DrawLine(start, end);
        }
    }

}
