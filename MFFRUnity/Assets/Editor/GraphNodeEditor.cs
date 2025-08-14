using System.Linq;
using UnityEditor;
using UnityEngine;
using System.IO;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using Assimp;


[CustomEditor(typeof(TorusSectionController))]
public class GraphNodeEditor : Editor
{
    private GraphEditorView view;
    private Vector2[] innerPointsToSave;
    private Vector2[] outerPointsToSave;
    private Vector2[] normalsToSave;
    private Vector2[] midpointsToSave;



    public override void OnInspectorGUI()
    {
        DrawDefaultInspector();
        TorusSectionController node = (TorusSectionController)target;



        Vector2[] inner = node.GetApproximatedPoints();
        Vector2[] outer = node.GetOffsetPoints(inner, node.Thickness);
        if (inner == null || inner.Length < 2) return;

        Rect rect = GUILayoutUtility.GetRect(300, 300);
        view = new GraphEditorView(rect, node.R_major, node.A_minor);

        Handles.BeginGUI();
        view.DrawBackground();
        view.DrawAxisWithTicks(node.R_major, node.A_minor);

        // トーラス断面（線のみ）
        view.DrawPolyline(inner.ToList(), Color.cyan);
        view.DrawPolyline(outer.ToList(), new Color(0.5f, 1f, 1f));

        // オレンジ線構成点
        float xL = node.R_major - 2 * node.A_minor;
        float xR = node.R_major + 2 * node.A_minor;
        Vector2 pL = new Vector2(0, node.InnerHeight);
        Vector2 pR = new Vector2(node.R_major * 10f, node.OuterHeight);

        Vector2? intersectP1 = IntersectionUtils.GetClosestIntersection(inner, pL, new Vector2(xR, node.InnerHeight), xL);
        Vector2? intersectP2 = IntersectionUtils.GetClosestIntersection(inner, new Vector2(xL, node.OuterHeight), pR, xR);

        if (intersectP1.HasValue && intersectP2.HasValue)
        {
            Vector2[] orangeLine = new Vector2[] { pL, intersectP1.Value, intersectP2.Value, pR };
            view.DrawPolyline(orangeLine.ToList(), new Color(1f, 0.5f, 0f), closed: false);

            // オレンジ線とトーラス断面の交点を抽出
            var clippedRegion = OrangeRegionExtractor.Extract(inner, orangeLine);
            int alignedEndIdx;
            // IdenticcalInboardが有効な場合、オレンジ線の交点を調整
            if (node.IdenticalInboard)
            {
                (clippedRegion, alignedEndIdx) = PointAlignmentUtils.AlignPointsLeftOfP1(clippedRegion, intersectP1.Value);
                // Debug.Log($"整列対象はインデックス {alignedEndIdx} まで");
                var (midpoints, normals) = NormalSegmentAnalyzer.AnalyzeSegmentNormals(clippedRegion, node.Segmentation, alignedEndIdx);
                view.DrawNormals(midpoints, normals);
                midpointsToSave = midpoints.Reverse().ToArray();
                normalsToSave = normals.Reverse().ToArray();
            }
            else
            {
                var (midpoints, normals) = NormalSegmentAnalyzer.AnalyzeSegmentNormals(clippedRegion, node.Segmentation, 999999);
                view.DrawNormals(midpoints, normals);
                midpointsToSave = midpoints.Reverse().ToArray();
                normalsToSave = normals.Reverse().ToArray();
            }
            view.DrawPolyline(clippedRegion.ToList(), Color.red, closed: false);
            // innerを保存対象の変数に、逆順にして格納
            innerPointsToSave = clippedRegion.Reverse().ToArray();


        }
        else
        {
            innerPointsToSave = null;
        }

        // outerとオレンジ線の交点を求める
        Vector2? intersectP1Outer = IntersectionUtils.GetClosestIntersection(outer, pL, new Vector2(xR, node.InnerHeight), xL);
        Vector2? intersectP2Outer = IntersectionUtils.GetClosestIntersection(outer, new Vector2(xL, node.OuterHeight), pR, xR);

        //innerと同様に、

        if (intersectP1Outer.HasValue && intersectP2Outer.HasValue)
        {
            Vector2[] orangeLine = new Vector2[] { pL, intersectP1Outer.Value, intersectP2Outer.Value, pR };

            // オレンジ線とトーラス断面の交点を抽出
            var clippedRegion = OrangeRegionExtractor.Extract(outer, orangeLine);
            int alignedEndIdx;
            // IdenticcalInboardが有効な場合、オレンジ線の交点を調整
            if (node.IdenticalInboard)
            {
                (clippedRegion, alignedEndIdx) = PointAlignmentUtils.AlignPointsLeftOfP1(clippedRegion, intersectP1Outer.Value);
                // Debug.Log($"整列対象はインデックス {alignedEndIdx} まで");

            }
            view.DrawPolyline(clippedRegion.ToList(), Color.red, closed: false);
            // outerを保存対象の変数に、逆順にして格納
            outerPointsToSave = clippedRegion.Reverse().ToArray();

        }
        else
        {
            outerPointsToSave = null;
        }




        // === 追加: 保存ボタン ===
        if (GUILayout.Button("Save Torus Description"))
        {
            SaveCurrentData();
        }
        if (GUILayout.Button("Generate Blanket Mesh"))
        {
            GenerateBlanketMesh(node);
        }


        Handles.EndGUI();
    }

    /// <summary>
    /// 現在の inner / outer / 法線データを保存
    /// </summary>
    private void SaveCurrentData()
    {
        //もし innerPointsToSave, outerPointsToSave, midpointsToSave, normalsToSaveのいずれかが null の場合は何もしない
        if (innerPointsToSave == null || outerPointsToSave == null || midpointsToSave == null || normalsToSave == null)
        {
            Debug.LogWarning("保存するデータが不完全です。");
            return;
        }

        // 保存先フォルダ（Unityプロジェクト/Assets/Torus/）
        string folder = Path.Combine(Application.dataPath, "Torus");

        // フォルダがなければ作成
        if (!Directory.Exists(folder))
        {
            Directory.CreateDirectory(folder);
        }

        // inner 保存
        File.WriteAllLines(Path.Combine(folder, "inner_unity.txt"),
            innerPointsToSave.Select(p => $"{p.x:F6},{p.y:F6}"));

        // outer 保存
        File.WriteAllLines(Path.Combine(folder, "outer_unity.txt"),
            outerPointsToSave.Select(p => $"{p.x:F6},{p.y:F6}"));

        // normals 保存
        using (StreamWriter sw = new StreamWriter(Path.Combine(folder, "normals_unity.txt")))
        {
            for (int i = 0; i < midpointsToSave.Length; i++)
            {
                sw.WriteLine($"{midpointsToSave[i].x:F6},{midpointsToSave[i].y:F6},{normalsToSave[i].x:F6},{normalsToSave[i].y:F6}");
            }
        }

        AssetDatabase.Refresh();
        Debug.Log("inner / outer / normals を保存しました: " + folder);
    }

    private void GenerateBlanketMesh(TorusSectionController node)
    {
        node.externalTool.RunUV(scriptFile: Path.Combine(Application.dataPath, @"..\..\mcp_robot2\blanket_generation.py"), directory: Path.Combine(Application.dataPath, @"..\..\mcp_robot2"));

    }
}
