using UnityEditor;
using UnityEngine;
using UnityEngine.UIElements;

[CustomEditor(typeof(GraphNode))]
public class GraphNodeEditor : Editor
{
    public override void OnInspectorGUI()
    {
        DrawDefaultInspector(); // pointCount, R, a, kappa, delta

        GraphNode node = (GraphNode)target;
        Vector2[] points = node.GetApproximatedPoints();
        if (points == null || points.Length < 2) return;

        Rect graphRect = GUILayoutUtility.GetRect(300, 300);
        EditorGUI.DrawRect(graphRect, new Color(0.1f, 0.1f, 0.1f));

        // データ範囲取得
        float minX = float.MaxValue, maxX = float.MinValue;
        float minZ = float.MaxValue, maxZ = float.MinValue;
        foreach (var p in points)
        {
            if (p.x < minX) minX = p.x;
            if (p.x > maxX) maxX = p.x;
            if (p.y < minZ) minZ = p.y;
            if (p.y > maxZ) maxZ = p.y;
        }

        Vector2 dataCenter = new Vector2((minX + maxX) / 2f, (minZ + maxZ) / 2f);
        float rangeX = maxX - minX;
        float rangeZ = maxZ - minZ;

        float margin = 1.2f; // 20% margin
        float scale = Mathf.Min(graphRect.width / (rangeX * margin), graphRect.height / (rangeZ * margin));
        Vector2 viewCenter = graphRect.center;

        Handles.BeginGUI();

        // 座標軸 + 目盛り
        DrawAxisWithTicks(viewCenter, dataCenter, scale, graphRect);

        // 線・点描画
        Handles.color = Color.cyan;
        for (int i = 0; i < points.Length; i++)
        {
            Vector2 p1 = viewCenter + (points[i] - dataCenter) * scale;
            Vector2 p2 = viewCenter + (points[(i + 1) % points.Length] - dataCenter) * scale;
            Handles.DrawLine(p1, p2);
            Handles.DrawSolidDisc(p1, Vector3.forward, 3f);
        }

        Handles.EndGUI();

        if (GUI.changed)
        {
            SavePointsToFile(points);
            EditorUtility.SetDirty(target);
        }

    }

    private void DrawAxisWithTicks(Vector2 viewCenter, Vector2 dataCenter, float scale, Rect rect)
    {
        int xMin = Mathf.FloorToInt((rect.xMin - viewCenter.x) / scale + dataCenter.x);
        int xMax = Mathf.CeilToInt((rect.xMax - viewCenter.x) / scale + dataCenter.x);
        int zMin = Mathf.FloorToInt((rect.yMin - viewCenter.y) / scale + dataCenter.y);
        int zMax = Mathf.CeilToInt((rect.yMax - viewCenter.y) / scale + dataCenter.y);

        Handles.color = Color.gray;

        // X軸目盛りとラベル
        for (int x = xMin; x <= xMax; x++)
        {
            Vector2 from = new Vector2(viewCenter.x + (x - dataCenter.x) * scale, rect.yMin);
            Vector2 to = new Vector2(viewCenter.x + (x - dataCenter.x) * scale, rect.yMax);
            Handles.DrawLine(from, to);

            if (x % 5 == 0)
                Handles.Label(new Vector2(from.x + 2, viewCenter.y + 4), $"{x}m", EditorStyles.miniLabel);
        }

        // Z軸目盛りとラベル
        for (int z = zMin; z <= zMax; z++)
        {
            Vector2 from = new Vector2(rect.xMin, viewCenter.y + (z - dataCenter.y) * scale);
            Vector2 to = new Vector2(rect.xMax, viewCenter.y + (z - dataCenter.y) * scale);
            Handles.DrawLine(from, to);

            if (z % 5 == 0)
                Handles.Label(new Vector2(viewCenter.x + 5, from.y - 8), $"{z}m", EditorStyles.miniLabel);
        }

        // 中央線（X軸・Z軸）
        Handles.color = Color.white;
        Handles.DrawLine(new Vector2(rect.xMin, viewCenter.y), new Vector2(rect.xMax, viewCenter.y)); // X軸
        Handles.DrawLine(new Vector2(viewCenter.x, rect.yMin), new Vector2(viewCenter.x, rect.yMax)); // Z軸



    }


    private void SavePointsToFile(Vector2[] points)
    {
        string directory = "Assets/Torus";
        string filePath = $"{directory}/torus_parameter.txt";

        // フォルダがなければ作成
        if (!System.IO.Directory.Exists(directory))
            System.IO.Directory.CreateDirectory(directory);

        using (System.IO.StreamWriter writer = new System.IO.StreamWriter(filePath, false))
        {
            writer.WriteLine("# x z");
            foreach (var p in points)
            {
                writer.WriteLine($"{p.x:F6} {p.y:F6}");
            }
        }

        // Unity上でファイル更新を検出させる
        AssetDatabase.Refresh();
    }
}


