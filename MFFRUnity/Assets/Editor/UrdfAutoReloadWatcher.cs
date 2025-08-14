#if UNITY_EDITOR
using System.Collections;
using System.IO;
using System.Threading.Tasks;
using Unity.EditorCoroutines.Editor;
using Unity.Robotics.UrdfImporter;
using Unity.Robotics.UrdfImporter.Editor;
using UnityEditor;
using UnityEngine;
using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Linq;



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
    

    private static IEnumerator ImportAndThen(string urdfFile, ImportSettings settings, Action<GameObject> onComplete)
    {
        IEnumerator<GameObject> importRoutine = UrdfRobotExtensions.Create(urdfFile, settings, true);

        GameObject result = null;
        while (importRoutine.MoveNext())
        {
            result = importRoutine.Current;  // 最後に返ってくるのが生成されたGameObject
            yield return null;
        }

        if (result != null)
        {
            onComplete?.Invoke(result); // 完了時にコールバック
        }
        else
        {
            Debug.LogWarning("URDF import returned null.");
        }
    }

    private static void ReloadUrdfModel()
    {
        GameObject existing = GameObject.Find("test_robot");
        if (existing != null)
        {
            UnityEngine.Object.DestroyImmediate(existing);
        }
        //string fullPath = Path.GetFullPath(urdfPath);
        //ImportRobotFromUrdf(fullPath);
        Debug.Log("Reloading URDF model...");
        string assetPath = "Assets/TemporaryRobotDescription/temporary_robot.urdf";
        //await Task.Delay(3000);

        if (Path.GetExtension(assetPath)?.ToLower() == ".urdf") //�����ɂ͓����Ă���
        {
            // Get existing open window or if none, make a new one:
            FileImportMenu window = (FileImportMenu)EditorWindow.GetWindow(typeof(FileImportMenu));
            // Change collision mesh decomposing method
            window.settings.convexMethod = ImportSettings.convexDecomposer.unity;

            window.urdfFile = UrdfAssetPathHandler.GetFullAssetPath(assetPath);
            window.minSize = new Vector2(500, 200);
            // window.Show();
            EditorCoroutineUtility.StartCoroutine(
                ImportAndThen(window.urdfFile, window.settings, imported =>
                {
                    Debug.Log($"URDF Import Complete. Imported GameObject: {imported.name}");
                    window.Close();
                    // ここに後続処理を書く
                    foreach (var collider in imported.GetComponentsInChildren<Collider>())
                    {
                        collider.enabled = false;
                    }
                    Debug.Log("All colliders disabled.");

                    foreach (var rb in imported.GetComponentsInChildren<Rigidbody>())
                    {
                        rb.isKinematic = true;
                        rb.detectCollisions = false;
                    }
                    foreach (var ab in imported.GetComponentsInChildren<ArticulationBody>())
                    {
                        ab.useGravity = false;
                    }

                    //もしbase*linkにマッチするGameObjectがあれば
                    Regex regex = new Regex(@"^base.*link$", RegexOptions.IgnoreCase);
                    var baseLink = imported.GetComponentsInChildren<Transform>().FirstOrDefault(t => regex.IsMatch(t.name));
                    if (baseLink != null)
                    {
                        //もしbaseLinkがurdf linkを持っていれば
                        var urdfLink = baseLink.GetComponent<UrdfLink>();
                        if (urdfLink != null)
                        {
                            urdfLink.IsBaseLink = true;
                        }

                        //もしbaseLinkがArticulationBodyを持っていれば
                        var articulationBody = baseLink.GetComponent<ArticulationBody>();
                        if (articulationBody != null)
                        {
                            articulationBody.immovable = true;

                        }

                    }
                }),
                window
            );


        }
        Debug.Log("Reloaded URDF model");

    }
}
#endif
