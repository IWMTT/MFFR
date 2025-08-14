using UnityEngine;
using UnityEditor;
using System.IO;
using System.Collections.Generic;

[InitializeOnLoad]
public class BlanketConfigurationWatcher : AssetPostprocessor
{
    private static readonly string CONFIG_FILE_PATH = "Assets/Torus/blanket_configuration.json";
    private static readonly string BLANKET_ENVIRONMENT_NAME = "BlanketEnvironment";
    private static readonly string MESH_FOLDER_PATH = "Assets/Torus/Mesh/";
    
    static BlanketConfigurationWatcher()
    {
        CheckAndUpdateBlanketConfiguration();
    }
    
    static void OnPostprocessAllAssets(string[] importedAssets, string[] deletedAssets, 
        string[] movedAssets, string[] movedFromAssetPaths)
    {
        foreach (string assetPath in importedAssets)
        {
            if (assetPath.Equals(CONFIG_FILE_PATH, System.StringComparison.OrdinalIgnoreCase))
            {
                Debug.Log($"[BlanketConfigurationWatcher] Detected changes in: {assetPath}");
                CheckAndUpdateBlanketConfiguration();
                break;
            }
        }
    }
    
    private static void CheckAndUpdateBlanketConfiguration()
    {
        if (!File.Exists(CONFIG_FILE_PATH))
        {
            Debug.LogWarning($"[BlanketConfigurationWatcher] Configuration file not found: {CONFIG_FILE_PATH}");
            return;
        }
        
        GameObject blanketEnvironment = GameObject.Find(BLANKET_ENVIRONMENT_NAME);
        if (blanketEnvironment == null)
        {
            Debug.LogWarning($"[BlanketConfigurationWatcher] BlanketEnvironment GameObject not found in scene");
            return;
        }
        
        ClearBlanketEnvironmentChildren(blanketEnvironment);
        ProcessBlanketConfiguration(blanketEnvironment);
    }
    
    private static void ClearBlanketEnvironmentChildren(GameObject blanketEnvironment)
    {
        int childCount = blanketEnvironment.transform.childCount;
        List<GameObject> childrenToDestroy = new List<GameObject>();
        
        for (int i = 0; i < childCount; i++)
        {
            childrenToDestroy.Add(blanketEnvironment.transform.GetChild(i).gameObject);
        }
        
        foreach (GameObject child in childrenToDestroy)
        {
            if (Application.isPlaying)
            {
                Object.Destroy(child);
            }
            else
            {
                Object.DestroyImmediate(child);
            }
        }
        
        Debug.Log($"[BlanketConfigurationWatcher] Cleared {childCount} children from BlanketEnvironment");
    }
    
    private static void ProcessBlanketConfiguration(GameObject blanketEnvironment)
    {
        try
        {
            string jsonContent = File.ReadAllText(CONFIG_FILE_PATH);
            Debug.Log($"[BlanketConfigurationWatcher] Processing configuration file...");
            
            BlanketConfigurationData configData = JsonUtility.FromJson<BlanketConfigurationData>(jsonContent);
            
            if (configData?.items == null || configData.items.Length == 0)
            {
                Debug.LogWarning("[BlanketConfigurationWatcher] No items found in configuration file");
                return;
            }
            
            Debug.Log($"[BlanketConfigurationWatcher] Found {configData.items.Length} items to process");
            
            int successCount = 0;
            foreach (BlanketItem item in configData.items)
            {
                if (CreateBlanketObject(blanketEnvironment, item))
                {
                    successCount++;
                }
            }
            
            Debug.Log($"[BlanketConfigurationWatcher] Successfully created {successCount}/{configData.items.Length} objects");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[BlanketConfigurationWatcher] Error processing configuration: {e.Message}");
        }
    }
    
    private static bool CreateBlanketObject(GameObject parent, BlanketItem item)
    {
        try
        {
            string meshPath = MESH_FOLDER_PATH + item.mesh;
            
            GameObject meshPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(meshPath);
            if (meshPrefab == null)
            {
                Debug.LogWarning($"[BlanketConfigurationWatcher] Mesh file not found: {meshPath}");
                return false;
            }

            GameObject newObject = Object.Instantiate(meshPrefab, parent.transform);

            newObject.name = item.name;

            // Z-up → Y-up 軸変換: X軸 -90° 回転を追加
            Quaternion zUpToYUp = Quaternion.Euler(-90, 0, 0);

            // その上で、Z軸回転（item.angle）を適用
            Quaternion angleRotation = Quaternion.Euler(0, item.angle, 0);

            newObject.transform.localRotation = angleRotation * zUpToYUp;
            newObject.transform.localPosition = Vector3.zero;
            newObject.transform.localScale = Vector3.one;

            Debug.Log($"[BlanketConfigurationWatcher] Created object: {item.name} (angle: {item.angle}, mesh: {item.mesh})");
            return true;
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[BlanketConfigurationWatcher] Error creating object '{item.name}': {e.Message}");
            return false;
        }
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
    public float angle;
    public string mesh;
}