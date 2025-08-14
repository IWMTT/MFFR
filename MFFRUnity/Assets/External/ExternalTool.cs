using UnityEngine;
using System.Diagnostics;
using System.IO;

[CreateAssetMenu(fileName = "ExternalTool", menuName = "Settings/External Tool")]
public class ExternalTool : ScriptableObject
{
    [Tooltip("uv の実行ファイルパス（空なら PATH から検索）")]
    public string uvExecutablePath = "uv"; // 初期値はPATH用

    /// <summary>
    /// uv を実行する
    /// </summary>
    /// <param name="scriptFile">実行するスクリプトファイル（例: "main.py"）</param>
    /// <param name="workingDirectory">スクリプトのある作業ディレクトリ</param>
    /// <param name="arguments">追加引数（例: "--help"）</param>
    public void RunUV(string scriptFile, string directory = null, string arguments = "")
    {
        string uvPath = ResolveExecutablePath();

        if (string.IsNullOrEmpty(uvPath))
        {
            UnityEngine.Debug.LogError("uv の実行ファイルが見つかりません。");
            return;
        }

        var process = new Process();
        process.StartInfo.FileName = uvPath;
        if (directory != null && !string.IsNullOrEmpty(directory))
        {
            process.StartInfo.Arguments = $"--directory {directory} run {scriptFile} {arguments}";
        }
        else
        {
            process.StartInfo.Arguments = $"run {scriptFile} {arguments}";
        }
        process.StartInfo.CreateNoWindow = true;
        process.StartInfo.UseShellExecute = false;
        process.StartInfo.RedirectStandardOutput = true;
        process.StartInfo.RedirectStandardError = true;
        string fullCommand = $"{process.StartInfo.FileName} {process.StartInfo.Arguments}";
        UnityEngine.Debug.Log($"[RunUV] 実行コマンド: {fullCommand}");

        process.OutputDataReceived += (sender, e) => { if (e.Data != null) UnityEngine.Debug.Log(e.Data); };
        process.ErrorDataReceived += (sender, e) => { if (e.Data != null) UnityEngine.Debug.LogError(e.Data); };

        try
        {
            process.Start();
            process.BeginOutputReadLine();
            process.BeginErrorReadLine();
        }
        catch (System.Exception ex)
        {
            UnityEngine.Debug.LogError($"uv 実行中にエラー: {ex.Message}");
        }
    }

    /// <summary>
    /// uv 実行ファイルのパスを解決する。空なら PATH から検索。
    /// </summary>
    private string ResolveExecutablePath()
    {
        // 設定されていればそのまま使う
        if (!string.IsNullOrWhiteSpace(uvExecutablePath) && File.Exists(ExpandEnvironmentVariables(uvExecutablePath)))
        {
            return ExpandEnvironmentVariables(uvExecutablePath);
        }

        // 設定されていないか、ファイルが見つからなければ PATH を探索
        try
        {
            var process = new Process();
            process.StartInfo.FileName = "where";
            process.StartInfo.Arguments = "uv";
            process.StartInfo.RedirectStandardOutput = true;
            process.StartInfo.UseShellExecute = false;
            process.StartInfo.CreateNoWindow = true;
            process.Start();

            string path = process.StandardOutput.ReadLine();
            process.WaitForExit();

            if (!string.IsNullOrEmpty(path) && File.Exists(path))
            {
                return path;
            }
        }
        catch
        {
            // 無視
        }

        return null;
    }

    private string ExpandEnvironmentVariables(string path)
    {
        return System.Environment.ExpandEnvironmentVariables(path);
    }
}
