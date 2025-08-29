using System.Collections;
using System.Collections.Generic;
using Unity.Collections;
using UnityEngine;
using UnityEditor;
using System.Runtime.InteropServices;
using Unity.VisualScripting;
using System.Linq;
using System.IO;
// using System.Text.Json;
using Newtonsoft.Json;
using System;
using UnityEngine.WSA;
using System.Runtime.CompilerServices;

public class BlanketToroidalDivisionController : MonoBehaviour
{
    [SerializeField]
    private int poloidalSegmentation = 18;


    [SerializeField, Range(1, 72)]
    private int toroidalSegmentation = 18;

    [SerializeField]
    private bool doubledOutboard = true;

    [SerializeField, Range(1, 36)]
    private int startOfOutBoard = 11;

    [SerializeField, Range(0, 180)]
    private float zShiftOfOutBoard = 10f;

    [SerializeField]
    private bool editIndividually = false;

    [SerializeField]
    private float slitWidth = 25f;

    [SerializeField]
    private Vector3[] blanketToroidalCoordinates = new Vector3[18];



    public int PoloidalSegmentation
    {
        get => poloidalSegmentation;
        set => poloidalSegmentation = Mathf.Max(1, value);
    }

    public int ToroidalSegmentation => toroidalSegmentation;

    public bool DoubledOutboard => doubledOutboard;

    public int StartOfOutBoard => startOfOutBoard;

    public float ZShiftOfOutBoard => zShiftOfOutBoard;

    public bool EditIndividually => editIndividually;

    public float SlitWidth => slitWidth;

    public Vector3[] BlanketToroidalCoordinates => blanketToroidalCoordinates;

    public void OnValidate()
    {
        //Edit indivisuallyがオフだったら、全ての要素を自動でセットする
        if (!editIndividually)
        {
            // BlanketToroidalCoordinates の、1列目の値を、360/ToroidalSegmentation で割った値にする
            if (blanketToroidalCoordinates != null && blanketToroidalCoordinates.Length > 0)
            {
                for (int i = 0; i < blanketToroidalCoordinates.Length; i++)
                {
                    blanketToroidalCoordinates[i].x = 360f / toroidalSegmentation;
                    blanketToroidalCoordinates[i].y = 360f / toroidalSegmentation - 0.5f;
                }
            }

            if (doubledOutboard && startOfOutBoard >= 1)
            {
                for (int i = startOfOutBoard - 1; i < blanketToroidalCoordinates.Length; i++)
                {
                    blanketToroidalCoordinates[i].x = 360f / toroidalSegmentation / 2;
                    blanketToroidalCoordinates[i].y = 360f / toroidalSegmentation / 2 - 0.5f;
                    blanketToroidalCoordinates[i].z = zShiftOfOutBoard;
                }
            }
        }

    }


    public void ChangeBlanketCoordinatesLength(int length)
    {
        if (blanketToroidalCoordinates.Length != length)
        {
            blanketToroidalCoordinates = new Vector3[length];
        }
    }

    private void Reset()
    {
        // 初期値を設定
        ChangeBlanketCoordinatesLength(toroidalSegmentation);
        OnValidate();

    }

}

[System.Serializable]
public class BlanketConfigurationData
{
    public BlanketItem[] items;
}

[System.Serializable] 
public class BlanketItem
{
    public string name;
    public float angle;  // zAngle から angle に変更
    public string mesh;  // meshPath から mesh に変更（ファイル名のみ）
}

[CustomEditor(typeof(BlanketToroidalDivisionController))]
public class BlanketToroidalDivisionControllerEditor : Editor
{

    public override void OnInspectorGUI()
    {
        var controller = (BlanketToroidalDivisionController)target;

        EditorGUI.BeginDisabledGroup(true);
        EditorGUILayout.IntField("Poloidal Segmentation", controller.PoloidalSegmentation);
        EditorGUI.EndDisabledGroup();


        // 編集可能なフィールド
        SerializedProperty toroidalProp = serializedObject.FindProperty("toroidalSegmentation");
        SerializedProperty slitWidthProp = serializedObject.FindProperty("slitWidth");
        SerializedProperty doubledOutboardProp = serializedObject.FindProperty("doubledOutboard");
        SerializedProperty startOfOutBoardProp = serializedObject.FindProperty("startOfOutBoard");
        SerializedProperty editIndividuallyProp = serializedObject.FindProperty("editIndividually");
        SerializedProperty blanketToroidalCoordinatesProp = serializedObject.FindProperty("blanketToroidalCoordinates");



        serializedObject.Update();
        EditorGUILayout.PropertyField(toroidalProp);
        EditorGUILayout.PropertyField(slitWidthProp, new GUIContent("Slit Width (mm)"));
        EditorGUILayout.PropertyField(doubledOutboardProp);
        if (controller.DoubledOutboard)
        {
            EditorGUILayout.PropertyField(startOfOutBoardProp, new GUIContent("Start of Outboard"));
            EditorGUILayout.PropertyField(serializedObject.FindProperty("zShiftOfOutBoard"), new GUIContent("Z Shift of Outboard (deg.)"));

        }
        EditorGUILayout.PropertyField(editIndividuallyProp);
        if (controller.EditIndividually)
        {
            SerializedProperty pointsProperty = serializedObject.FindProperty("blanketToroidalCoordinates");

            // ヘッダー行を先に表示
            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.LabelField("Row", GUILayout.Width(50));
            EditorGUILayout.LabelField("Toroidal Angle (deg.)", GUILayout.Width(150));
            EditorGUILayout.LabelField("", GUILayout.Width(50));  // 空欄
            EditorGUILayout.LabelField("Extrude Angle (deg.)\nDefault: Toroidal Angle - 0.5", GUILayout.Width(150));
            EditorGUILayout.LabelField("", GUILayout.Width(50));  // 空欄
            EditorGUILayout.LabelField("Shift around z-axis (deg.)", GUILayout.Width(150));
            EditorGUILayout.LabelField("", GUILayout.Width(50));  // 空欄
            EditorGUILayout.EndHorizontal();

            // 各データ行
            for (int i = 0; i < controller.BlanketToroidalCoordinates.Length; i++)
            {
                SerializedProperty point = pointsProperty.GetArrayElementAtIndex(i);
                SerializedProperty x = point.FindPropertyRelative("x");
                SerializedProperty y = point.FindPropertyRelative("y");
                SerializedProperty z = point.FindPropertyRelative("z");

                EditorGUILayout.BeginHorizontal("box");
                EditorGUILayout.LabelField($"Row {i + 1}", GUILayout.Width(50));
                x.floatValue = EditorGUILayout.FloatField("", x.floatValue, GUILayout.Width(50));
                GUILayout.Space(100);  // タイトルとの幅調整
                y.floatValue = EditorGUILayout.FloatField("", y.floatValue, GUILayout.Width(50));
                GUILayout.Space(100);  // タイトルとの幅調整
                z.floatValue = EditorGUILayout.FloatField("", z.floatValue, GUILayout.Width(50));
                GUILayout.Space(100);
                EditorGUILayout.EndHorizontal();
            }
        }
        else
        {
            EditorGUI.BeginDisabledGroup(true);
            SerializedProperty pointsProperty = serializedObject.FindProperty("blanketToroidalCoordinates");

            // ヘッダー行を先に表示
            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.LabelField("Row", GUILayout.Width(50));
            EditorGUILayout.LabelField("Toroidal Angle (deg.)", GUILayout.Width(150));
            EditorGUILayout.LabelField("", GUILayout.Width(50));  // 空欄
            EditorGUILayout.LabelField("Extrude Angle (deg.)\nDefault: Toroidal Angle - 0.5", GUILayout.Width(150));
            EditorGUILayout.LabelField("", GUILayout.Width(50));  // 空欄
            EditorGUILayout.LabelField("Shift around z-axis (deg.)", GUILayout.Width(150));
            EditorGUILayout.LabelField("", GUILayout.Width(50));  // 空欄
            EditorGUILayout.EndHorizontal();

            // 各データ行
            for (int i = 0; i < controller.BlanketToroidalCoordinates.Length; i++)
            {
                SerializedProperty point = pointsProperty.GetArrayElementAtIndex(i);
                SerializedProperty x = point.FindPropertyRelative("x");
                SerializedProperty y = point.FindPropertyRelative("y");
                SerializedProperty z = point.FindPropertyRelative("z");

                EditorGUILayout.BeginHorizontal("box");
                EditorGUILayout.LabelField($"Row {i + 1}", GUILayout.Width(50));
                x.floatValue = EditorGUILayout.FloatField("", x.floatValue, GUILayout.Width(50));
                GUILayout.Space(100);  // タイトルとの幅調整
                y.floatValue = EditorGUILayout.FloatField("", y.floatValue, GUILayout.Width(50));
                GUILayout.Space(100);  // タイトルとの幅調整
                z.floatValue = EditorGUILayout.FloatField("", z.floatValue, GUILayout.Width(50));
                GUILayout.Space(100);
                EditorGUILayout.EndHorizontal();
            }
            EditorGUI.EndDisabledGroup();
        }

        if (GUILayout.Button("Save Toroidal Description"))
        {
            SaveCurrentData(controller);
        }

        if (GUILayout.Button("Generate New Blanket Meshes"))
        {
            AssetDatabase.StartAssetEditing();
            ExternalTool tool = ScriptableObject.CreateInstance<ExternalTool>();
            tool.RunUV(scriptFile: "blanket_generation.py", directory: "../mcp_robot2/", arguments: "");
            AssetDatabase.StopAssetEditing();
            AssetDatabase.Refresh();

        }


        serializedObject.ApplyModifiedProperties();

    }

    private void SaveCurrentData(BlanketToroidalDivisionController controller)
    {
        // 保存処理を実装
        string folder = Path.Combine(UnityEngine.Application.dataPath, "Torus");
        if (!Directory.Exists(folder))
        {
            Directory.CreateDirectory(folder);
        }

        // blanketToroidalCoordinates を保存
        File.WriteAllLines(Path.Combine(folder, "blanket_toroidal_coordinates.txt"),
            controller.BlanketToroidalCoordinates.Select(p => $"{p.x:F6},{p.y:F6},{p.z:F6}"));

        // 各ブランケットの角度情報を保存
        List<string> names = new List<string>();
        List<float> zAngles = new List<float>();
        List<string> meshPaths = new List<string>();
        int fullSegments = controller.PoloidalSegmentation;
        int outboardStartIndex = Mathf.Clamp(controller.StartOfOutBoard, 1, fullSegments);
        int inboardCount = outboardStartIndex - 1;
        int outboardCount = fullSegments - inboardCount;


        int rowIndex = 1;

        // Inboard: SB01C01, SB02C02, ...
        for (int i = 0; i < outboardStartIndex - 1; i++)
        {
            // toroidal angle(BlanketToroidalCoordinates[i].x)を取得し、その数で、360を割る
            float toroidalAngle = controller.BlanketToroidalCoordinates[i].x;
            float angle = controller.BlanketToroidalCoordinates[i].z; //最初にオフセット角度を記録。そのあと、for文の中で、何度ごとかを足している
            int columns = (int)(360f / toroidalAngle);
            for (int j = 0; j < columns; j++)
            {
                // Name of blanket module
                string sb = $"SB{rowIndex:D2}";
                string name = $"{sb}C{j + 1:D2}";
                names.Add(name);

                // z-axis angle
                zAngles.Add(angle);
                angle += toroidalAngle;

                // mesh path
                meshPaths.Add($"BLKT_{rowIndex}.gltf");
            }
            rowIndex++;
        }

        // Outboard: SBxxCyy, SBxxSyy, ...
        for (int i = outboardStartIndex - 1; i < controller.BlanketToroidalCoordinates.Length; i++)
        {
            // toroidal angle(BlanketToroidalCoordinates[i].x)を取得し、その数で、360を割る
            float toroidalAngle = controller.BlanketToroidalCoordinates[i].x;
            float angle = controller.BlanketToroidalCoordinates[i].z;
            int columns = (int)(360f / toroidalAngle / 2);

            for (int j = 0; j < columns; j++)
            {
                string sb1 = $"SB{rowIndex:D2}";
                names.Add($"{sb1}C{j + 1:D2}");
                // z-axis angle
                zAngles.Add(angle);
                angle += toroidalAngle;

                // mesh path
                meshPaths.Add($"BLKT_{rowIndex}.gltf");



                string sb2 = $"SB{rowIndex:D2}";
                names.Add($"{sb2}S{j + 1:D2}");
                // z-axis angle
                zAngles.Add(angle);
                angle += toroidalAngle;

                // mesh path
                meshPaths.Add($"BLKT_{rowIndex}.gltf");


            }
            rowIndex++;
            SaveToJson(names, zAngles, meshPaths, Path.Combine(folder, "blanket_configuration.json"));

        }

        Debug.Log("Blanket Names: " + string.Join(", ", names));
        Debug.Log("Blanket Z-Angles: " + string.Join(", ", zAngles));

        // //blanket_configuration.jsonを保存
        // string configFilePath = Path.Combine(folder, "blanket_configuration.json");

        AssetDatabase.Refresh();
        Debug.Log("Blanket Toroidal Coordinates saved to: " + folder);
    }

void SaveToJson(List<string> names, List<float> zAngles, List<string> meshPaths, string path)
{
    if (names.Count != zAngles.Count || names.Count != meshPaths.Count)
    {
        throw new Exception("名前、角度、メッシュパスのリストの長さが一致しません");
    }
    
    // BlanketItemのリストを作成
    List<BlanketItem> items = new List<BlanketItem>();
    for (int i = 0; i < names.Count; i++)
    {
        // meshPathsからファイル名のみを抽出（パスの場合）
        string meshFileName = System.IO.Path.GetFileName(meshPaths[i]);
        
        items.Add(new BlanketItem
        {
            name = names[i],
            angle = zAngles[i],
            mesh = meshFileName  // ファイル名のみを保存
        });
    }
    
    // BlanketConfigurationDataでラップ
    BlanketConfigurationData configData = new BlanketConfigurationData
    {
        items = items.ToArray()
    };
    
    // JSONとしてシリアライズ
    string json = JsonConvert.SerializeObject(configData, Formatting.Indented);
    File.WriteAllText(path, json);
    
    Debug.Log($"[BlanketToroidalDivisionController] Saved {items.Count} items to {path}");
}

}
