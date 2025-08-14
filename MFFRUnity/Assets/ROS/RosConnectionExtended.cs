using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using UnityEditor;


public class RosConnectionExtended : ROSConnection
{

    [SerializeField]
    private string containerName = "ROSContainer";

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {

    }
}

// Editior
#if UNITY_EDITOR


[CustomEditor(typeof(RosConnectionExtended))]
public class RosConnectionExtendedEditor : Editor
{
    public override void OnInspectorGUI()
    {
        DrawDefaultInspector();

        var type = typeof(RosConnectionExtended);
        var field = type.GetField("containerName", System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Public);
        if (field != null)
        {
            EditorGUILayout.LabelField("Container Name", field.GetValue(null)?.ToString());
        }
    }
}
#endif
