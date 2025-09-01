#if UNITY_EDITOR
using System.Collections.Generic;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;

public class BlanketMatrixViewer : MonoBehaviour
{
    [Tooltip("このオブジェクト直下（または指定ルート直下）の子を走査し、SB{row}{C|S}{col} をマトリクス表示します。")]
    public Transform blanketEnvironmentRoot; // 未指定なら自分自身

    [Range(1, 99)] public int maxRowClamp = 18;
    [Range(1, 99)] public int maxColClamp = 18;

    // インスペクターからは操作させないが、スクリプト上では変更可能
    [HideInInspector] public int cellSize = 22;

    [Header("UI")]
    public bool drawGridBoxes = true;

    // 内部キャッシュ
    [System.NonSerialized] public Dictionary<(int row, char type, int col), GameObject> map
        = new Dictionary<(int, char, int), GameObject>();
    [System.NonSerialized] public int maxRowFound = 0;
    [System.NonSerialized] public int maxColFound = 0;
}

[CustomEditor(typeof(BlanketMatrixViewer))]
public class BlanketMatrixViewerEditor : Editor
{
    private static readonly Regex NameRx =
        new Regex(@"^SB(?<row>\d{2})(?<type>[CS])(?<col>\d{2})$", RegexOptions.Compiled);

    private Vector2 _scroll;

    public override void OnInspectorGUI()
    {
        var viewer = (BlanketMatrixViewer)target;

        if (viewer.blanketEnvironmentRoot == null)
            viewer.blanketEnvironmentRoot = viewer.transform;

        EditorGUILayout.Space(4);
        EditorGUILayout.LabelField("Blanket Matrix Viewer", EditorStyles.boldLabel);
        EditorGUILayout.PropertyField(serializedObject.FindProperty("blanketEnvironmentRoot"));
        EditorGUILayout.PropertyField(serializedObject.FindProperty("maxRowClamp"));
        EditorGUILayout.PropertyField(serializedObject.FindProperty("maxColClamp"));
        EditorGUILayout.PropertyField(serializedObject.FindProperty("drawGridBoxes"));
        serializedObject.ApplyModifiedProperties();

        using (new EditorGUILayout.HorizontalScope())
        {
            if (GUILayout.Button("Refresh", GUILayout.Height(22)))
                RebuildMap(viewer);

            if (GUILayout.Button("Select Root", GUILayout.Height(22)))
            {
                Selection.activeObject = viewer.blanketEnvironmentRoot != null
                    ? viewer.blanketEnvironmentRoot.gameObject
                    : viewer.gameObject;
                EditorGUIUtility.PingObject(Selection.activeObject);
            }
        }

        if (viewer.map.Count == 0 && Event.current.type == EventType.Repaint)
            RebuildMap(viewer);

        EditorGUILayout.Space(6);
        DrawMatrix(viewer);
    }

    private void RebuildMap(BlanketMatrixViewer viewer)
    {
        viewer.map.Clear();
        viewer.maxRowFound = 0;
        viewer.maxColFound = 0;

        var root = viewer.blanketEnvironmentRoot != null ? viewer.blanketEnvironmentRoot : viewer.transform;
        if (root == null)
        {
            EditorGUILayout.HelpBox("Root transform is null.", MessageType.Warning);
            return;
        }

        foreach (Transform child in root)
        {
            var m = NameRx.Match(child.name);
            if (!m.Success) continue;

            int row = int.Parse(m.Groups["row"].Value);
            char type = m.Groups["type"].Value[0]; // 'C' or 'S'
            int col = int.Parse(m.Groups["col"].Value);

            if (row < 1 || row > viewer.maxRowClamp) continue;
            if (col < 1 || col > viewer.maxColClamp) continue;

            viewer.map[(row, type, col)] = child.gameObject;
            if (row > viewer.maxRowFound) viewer.maxRowFound = row;
            if (col > viewer.maxColFound) viewer.maxColFound = col;
        }

        if (viewer.maxRowFound == 0) viewer.maxRowFound = 1;
        if (viewer.maxColFound == 0) viewer.maxColFound = 1;

        Repaint();
    }

private void DrawMatrix(BlanketMatrixViewer viewer)
{
    // 固定・共有パラメータ
    int cell = Mathf.Max(12, viewer.cellSize);  // 22 を想定
    int gap  = 2;                               // セル間の水平/垂直スペース
    int rowLabelW = cell + 6;                   // 行ラベルの幅（左余白込み）
    int headerH   = cell;                       // ヘッダ行の高さ（= セル高）

    // グリッド寸法（C/Sは2列ワンセット）
    int pairCount = viewer.maxColFound;             // C/S の番号カウント
    int gridCols  = pairCount * 2;                  // 実セル列数（CとSで2倍）
    int gridRows  = viewer.maxRowFound;             // 実セル行数

    // 全体サイズ（最後のセル後に余計な gap を足さないために -gap）
    float totalW = rowLabelW + gridCols * (cell + gap) - gap;
    float totalH = headerH  + gridRows * (cell + gap) - gap;

    // スクロールビュー確保
    _scroll = EditorGUILayout.BeginScrollView(
        _scroll,
        GUILayout.Height(Mathf.Clamp((int)totalH + 8, 80, 600))
    );

    // 描画領域を予約し、その中でローカル(0,0)座標で描く
    Rect area = GUILayoutUtility.GetRect(totalW, totalH, GUILayout.ExpandWidth(false));
    GUI.BeginGroup(area);

    // スタイル（margin/padding を殺してズレ要因を除去）
    var labelCenter = new GUIStyle(EditorStyles.miniLabel)
    {
        alignment = TextAnchor.MiddleCenter,
        margin = new RectOffset(0,0,0,0),
        padding = new RectOffset(0,0,0,0)
    };
    var boxStyle = new GUIStyle(GUI.skin.box)
    {
        margin = new RectOffset(0,0,0,0),
        padding = new RectOffset(0,0,0,0)
    };

    // 位置計算ヘルパ
    Rect PairHeaderRect(int pairIdx) // pairIdx: 0..(pairCount-1)
    {
        // C列のXを基準に「2セル幅 + gap ひとつ分」でヘッダ（C/Sxx）を載せる
        float xC = rowLabelW + (pairIdx * 2) * (cell + gap);
        float w  = (cell + gap) + cell; // Cセル幅 + gap + Sセル幅 ＝ cell*2 + gap
        return new Rect(xC, 0, w, headerH);
    }

    Rect CellRect(int rowIdx, int colIdx) // colIdx: 0..(gridCols-1), rowIdx: 0..(gridRows-1)
    {
        float x = rowLabelW + colIdx * (cell + gap);
        float y = headerH  + rowIdx * (cell + gap);
        return new Rect(x, y, cell, cell);
    }

    Rect RowLabelRect(int rowIdx)
    {
        float y = headerH + rowIdx * (cell + gap);
        return new Rect(0, y, rowLabelW, cell);
    }

    // 1) ヘッダ行（C/Sxx）
    for (int p = 0; p < pairCount; p++)
    {
        var hr = PairHeaderRect(p);
        // 端数丸めでサブピクセル誤差を避ける（DPI環境でも崩れにくくなる）
        hr.x  = Mathf.Round(hr.x);  hr.y  = Mathf.Round(hr.y);
        hr.width  = Mathf.Round(hr.width);  hr.height = Mathf.Round(hr.height);

        GUI.Label(hr, $"C/S{(p+1):00}", labelCenter);
    }

    // 2) 本体（行ラベル＋セル群）
    for (int r = 0; r < gridRows; r++)
    {
        // 行ラベル（数字のみ）
        var rr = RowLabelRect(r);
        rr.x = Mathf.Round(rr.x); rr.y = Mathf.Round(rr.y);
        rr.width = Mathf.Round(rr.width); rr.height = Mathf.Round(rr.height);
        GUI.Label(rr, $"{(r+1):00}", labelCenter);

        // 各列（CとS）
        for (int c = 0; c < gridCols; c++)
        {
            var cr = CellRect(r, c);
            cr.x = Mathf.Round(cr.x); cr.y = Mathf.Round(cr.y);
            cr.width = Mathf.Round(cr.width); cr.height = Mathf.Round(cr.height);

            if (viewer.drawGridBoxes) GUI.Box(cr, GUIContent.none, boxStyle);

            // クリック可能に（存在セルのみ反応）
            // C/S の判定：偶数列= C, 奇数列= S
            char type = (c % 2 == 0) ? 'C' : 'S';
            int  colNo = (c / 2) + 1;       // 1..maxColFound
            int  rowNo = r + 1;            // 1..maxRowFound

            if (viewer.map.TryGetValue((rowNo, type, colNo), out var go) && go != null)
            {
                if (GUI.Button(cr, GUIContent.none))
                {
                    Selection.activeGameObject = go;
                    EditorGUIUtility.PingObject(go);
                }
            }
        }
    }

    GUI.EndGroup();
    EditorGUILayout.EndScrollView();
}
    private void DrawCell(BlanketMatrixViewer viewer, int row, char type, int col,
                          int cell, GUIStyle boxStyle)
    {
        viewer.map.TryGetValue((row, type, col), out var go);
        Rect rect = GUILayoutUtility.GetRect(cell, cell, GUILayout.Width(cell), GUILayout.Height(cell));

        if (viewer.drawGridBoxes)
            GUI.Box(rect, GUIContent.none, boxStyle);

        if (go != null)
        {
            if (GUI.Button(rect, GUIContent.none)) // 中身あり：クリックで選択 & Ping
            {
                Selection.activeGameObject = go;
                EditorGUIUtility.PingObject(go);
            }
        }
        // 中身なし：枠のみ（何も描かない）
    }
}
#endif
