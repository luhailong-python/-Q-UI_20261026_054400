using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace YifuArt.Editor
{
    public static class DaoProjectBuilder
    {
        private const string Output = "Assets/Generated";
        [InitializeOnLoadMethod]
        private static void FirstOpen() { EditorApplication.delayCall += AutoBuild; }
        private static void AutoBuild()
        {
            if (EditorApplication.isCompiling || EditorApplication.isUpdating) { EditorApplication.delayCall += AutoBuild; return; }
            if (!File.Exists("Library/DaoArtSetup-v1.ok")) BuildAndValidate();
        }
        [MenuItem("一符镇万妖/生成资源接入场景与预制体")]
        public static void BuildAndValidate()
        {
            try
            {
                var data = ArtCatalog.Data;
                foreach (var art in data.assets)
                {
                    AssetDatabase.ImportAsset("Assets/Resources/" + art.resource + ".png", ImportAssetOptions.ForceUpdate);
                    if (art.textureOnly)
                    {
                        if (ArtCatalog.Texture(art.id) == null) throw new Exception("Missing texture " + art.id);
                    }
                    else ArtCatalog.Sprite(art.id);
                }
                foreach (string name in new[] { "NotoSansCJKsc-Regular.otf", "MaShanZheng-Regular.ttf" })
                {
                    string fontPath = "Assets/Resources/DaoFonts/" + name;
                    AssetDatabase.ImportAsset(fontPath, ImportAssetOptions.ForceUpdate);
                    if (AssetDatabase.LoadAssetAtPath<Font>(fontPath) == null) throw new Exception("Missing font " + name);
                }
                Directory.CreateDirectory(Output + "/Animations");
                Directory.CreateDirectory("Assets/Resources/DaoActors");
                Directory.CreateDirectory("Assets/Scenes"); AssetDatabase.Refresh();
                foreach (var actor in data.actors) BuildActor(actor);
                var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
                EditorSceneManager.SaveScene(scene, "Assets/Scenes/ArtIntegration.unity");
                EditorSceneManager.CloseScene(scene, true);
                EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene("Assets/Scenes/ArtIntegration.unity", true) };
                PlayerSettings.productName = "一符镇万妖";
                PlayerSettings.defaultInterfaceOrientation = UIOrientation.AutoRotation;
                PlayerSettings.allowedAutorotateToLandscapeLeft = PlayerSettings.allowedAutorotateToLandscapeRight = true;
                PlayerSettings.allowedAutorotateToPortrait = true; PlayerSettings.allowedAutorotateToPortraitUpsideDown = false;
                AssetDatabase.SaveAssets();
                File.WriteAllText("Library/DaoArtSetup-v1.ok", DateTime.UtcNow.ToString("o"));
                WriteReport(true, "Imported textures/sprites and generated11Prefab/22clips/11controllers and1scene.");
                Debug.Log("Dao art integration assets generated. Open ArtIntegration scene and press Play for runtime review.");
            }
            catch (Exception error) { WriteReport(false, error.ToString()); Debug.LogException(error); throw; }
        }
        private static void BuildActor(ActorRow row)
        {
            string root = Output + "/Animations/" + row.id;
            var idle = MakeClip(root + "_idle.anim", row, false);
            var walk = MakeClip(root + "_walk.anim", row, true);
            string controllerPath = root + ".controller";
            if (AssetDatabase.LoadAssetAtPath<AnimatorController>(controllerPath) != null) AssetDatabase.DeleteAsset(controllerPath);
            var controller = AnimatorController.CreateAnimatorControllerAtPath(controllerPath);
            controller.AddParameter("Walking", AnimatorControllerParameterType.Bool);
            var sm = controller.layers[0].stateMachine;
            var idleState = sm.AddState("Idle"); idleState.motion = idle;
            var walkState = sm.AddState("Walk"); walkState.motion = walk; sm.defaultState = idleState;
            var toWalk = idleState.AddTransition(walkState); toWalk.hasExitTime = false; toWalk.duration = 0;
            toWalk.AddCondition(AnimatorConditionMode.If, 0, "Walking");
            var toIdle = walkState.AddTransition(idleState); toIdle.hasExitTime = false; toIdle.duration = 0;
            toIdle.AddCondition(AnimatorConditionMode.IfNot, 0, "Walking");
            var go = new GameObject(row.id);
            go.AddComponent<SpriteRenderer>().sprite = ArtCatalog.Sprite(row.frames[0]);
            go.AddComponent<Animator>().runtimeAnimatorController = controller;
            go.AddComponent<ArtActor>().actorId = row.id;
            PrefabUtility.SaveAsPrefabAsset(go, "Assets/Resources/DaoActors/" + row.id + ".prefab");
            UnityEngine.Object.DestroyImmediate(go);
        }
        private static AnimationClip MakeClip(string path, ActorRow row, bool moving)
        {
            if (AssetDatabase.LoadAssetAtPath<AnimationClip>(path) != null) AssetDatabase.DeleteAsset(path);
            var clip = new AnimationClip { name = row.id + (moving ? "_walk" : "_idle"), frameRate = 60 };
            int n = moving ? row.frames.Length : 1;
            var keys = new ObjectReferenceKeyframe[n + 1]; float time = 0;
            for (int i = 0; i < n; i++)
            {
                keys[i] = new ObjectReferenceKeyframe { time = time, value = ArtCatalog.Sprite(row.frames[i]) };
                time += moving ? row.seconds[i] : .1f;
            }
            keys[n] = new ObjectReferenceKeyframe { time = time, value = ArtCatalog.Sprite(row.frames[0]) };
            AnimationUtility.SetObjectReferenceCurve(clip, EditorCurveBinding.PPtrCurve("", typeof(SpriteRenderer), "m_Sprite"), keys);
            var settings = AnimationUtility.GetAnimationClipSettings(clip); settings.loopTime = true;
            AnimationUtility.SetAnimationClipSettings(clip, settings);
            AssetDatabase.CreateAsset(clip, path); return clip;
        }
        private static void WriteReport(bool passed, string message)
        {
            Directory.CreateDirectory("IntegrationReports");
            var report = new BuildReport { passed = passed, editorVersion = Application.unityVersion, timestampUtc = DateTime.UtcNow.ToString("o"), message = message };
            File.WriteAllText("IntegrationReports/editor-import.json", JsonUtility.ToJson(report, true));
        }
        [Serializable] private class BuildReport { public bool passed; public string editorVersion, timestampUtc, message; }
    }
}
