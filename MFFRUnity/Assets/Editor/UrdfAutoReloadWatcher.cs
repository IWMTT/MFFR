#if UNITY_EDITOR
using System.IO;
using System.Threading.Tasks;
using Unity.EditorCoroutines.Editor;
using Unity.Robotics.UrdfImporter;
using Unity.Robotics.UrdfImporter.Editor;
using UnityEditor;
using UnityEngine;



[InitializeOnLoad]
public static class UrdfAutoReloadWatcher
{
    static FileSystemWatcher urdfWatcher;
    static FileSystemWatcher meshWatcher;

    static string urdfPath = "Assets/TemporaryRobotDescription/temporary_robot.urdf";

    static UrdfAutoReloadWatcher()
    {
        StartWatching();
    }

    public static void StartWatching()
    {
        urdfWatcher = new FileSystemWatcher(Path.GetDirectoryName(urdfPath), "*.urdf");
        urdfWatcher.Changed += OnChanged;
        urdfWatcher.EnableRaisingEvents = true;

        //meshWatcher = new FileSystemWatcher(meshFolder);
        //meshWatcher.Filter = "*.*";
        //meshWatcher.NotifyFilter = NotifyFilters.LastWrite;
        //meshWatcher.Changed += OnChanged;
        //meshWatcher.EnableRaisingEvents = true;
    }

    private static void OnChanged(object sender, FileSystemEventArgs e)
    {
        Debug.Log($"URDF or mesh file changed: {e.FullPath}");
        EditorApplication.delayCall += () =>
        {
            ReloadUrdfModel();
        };
    }

    private static void ReloadUrdfModel()
    {
        // 古いモデル削除（ヒエラルキー上の "robot" オブジェクトなど）
        GameObject existing = GameObject.Find("test_robot");
        if (existing != null)
        {
            Object.DestroyImmediate(existing);
        }

        //// URDF 再読み込み（パスは URDF に合わせて変更）
        //string fullPath = Path.GetFullPath(urdfPath);
        //ImportRobotFromUrdf(fullPath);
        Debug.Log("Reloading URDF model...");
        string assetPath = "Assets/TemporaryRobotDescription/temporary_robot.urdf";
        //await Task.Delay(3000);

        if (Path.GetExtension(assetPath)?.ToLower() == ".urdf") //ここには入っている
        {
            // Get existing open window or if none, make a new one:
            FileImportMenu window = (FileImportMenu)EditorWindow.GetWindow(typeof(FileImportMenu));
            window.urdfFile = UrdfAssetPathHandler.GetFullAssetPath(assetPath);
            window.minSize = new Vector2(500, 200);
            window.Show();
            EditorCoroutineUtility.StartCoroutine(UrdfRobotExtensions.Create(window.urdfFile, window.settings, true), window);
            //string urdfFile = UrdfAssetPathHandler.GetFullAssetPath(assetPath);
            //ImportSettings settings = new ImportSettings();
            //UrdfRobotExtensions.Create(urdfFile, settings, false);
            //Debug.Log("URDF model reloaded successfully.");
            window.Close();


        }
        Debug.Log("Reloaded URDF model");

    }
}
#endif
