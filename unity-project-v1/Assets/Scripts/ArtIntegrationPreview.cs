using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using UnityEngine.SceneManagement;

namespace YifuArt
{
    public sealed class PreviewDragInput : MonoBehaviour, IPointerDownHandler, IDragHandler, IPointerUpHandler
    {
        private Vector2 origin;
        public Vector2 Direction { get; private set; }
        public void OnPointerDown(PointerEventData e) { origin = e.position; Direction = Vector2.zero; }
        public void OnDrag(PointerEventData e) { Direction = Vector2.ClampMagnitude((e.position - origin) / 120f, 1); }
        public void OnPointerUp(PointerEventData e) { Direction = Vector2.zero; }
    }
    public sealed class ArtIntegrationPreview : MonoBehaviour
    {
        private Canvas canvas;
        private CanvasScaler scaler;
        private Camera cameraView;
        private Font font;
        private RectTransform page;
        private GameObject world;
        private ArtActor controlled;
        private PreviewDragInput drag;
        private string selected = "hero_daotong";
        private bool portrait, playing = true, slow;
        private int mode;
        private Text status;
        private Material groundMaterial;
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void StartPreview()
        {
            if (SceneManager.GetActiveScene().name != "ArtIntegration") return;
            if (Object.FindFirstObjectByType<ArtIntegrationPreview>() == null)
                new GameObject("DaoArtIntegrationPreview").AddComponent<ArtIntegrationPreview>();
        }
        private void Awake()
        {
            cameraView = Camera.main;
            if (cameraView == null)
            {
                cameraView = new GameObject("Main Camera").AddComponent<Camera>();
                cameraView.tag = "MainCamera";
            }
            cameraView.orthographic = true;
            cameraView.backgroundColor = new Color(.91f, .88f, .78f);
            cameraView.transform.position = new Vector3(0, 0, -10);
            font = Resources.Load<Font>("DaoFonts/NotoSansCJKsc-Regular");
            if (font == null) throw new System.InvalidOperationException("Missing bundled Chinese font");
            if (EventSystem.current == null)
                new GameObject("EventSystem", typeof(EventSystem), typeof(StandaloneInputModule));
            canvas = new GameObject("DaoCanvas", typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster)).GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            scaler = canvas.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            portrait = Screen.height > Screen.width;
            ApplyOrientation();
            ShowMenu();
        }
        private void ApplyOrientation()
        {
            scaler.referenceResolution = portrait ? new Vector2(1080, 1920) : new Vector2(1920, 1080);
            scaler.matchWidthOrHeight = .5f;
            cameraView.orthographicSize = portrait ? 6.8f : 5.4f;
        }
        private void Update()
        {
            bool p = Screen.height > Screen.width;
            if (p != portrait)
            {
                portrait = p; ApplyOrientation();
                if (mode == 0) ShowMenu(); else if (mode == 1) ShowAllActors();
            }
            if (mode == 2 && controlled != null)
            {
                Vector2 input = drag != null ? drag.Direction : Vector2.zero;
                if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow)) input.x -= 1;
                if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow)) input.x += 1;
                if (Input.GetKey(KeyCode.W) || Input.GetKey(KeyCode.UpArrow)) input.y += 1;
                if (Input.GetKey(KeyCode.S) || Input.GetKey(KeyCode.DownArrow)) input.y -= 1;
                controlled.Move(playing ? Vector2.ClampMagnitude(input, 1) * (2.5f * Time.deltaTime) : Vector2.zero);
                Vector3 position = controlled.transform.position;
                cameraView.transform.position = new Vector3(position.x, position.y, -10);
            }
            if (Input.GetKeyDown(KeyCode.Escape)) ShowMenu();
        }
        private RectTransform Rect(string name, Transform parent, Vector2 anchor, Vector2 position, Vector2 size)
        {
            var r = new GameObject(name, typeof(RectTransform)).GetComponent<RectTransform>();
            r.SetParent(parent, false); r.anchorMin = r.anchorMax = anchor;
            r.anchoredPosition = position; r.sizeDelta = size;
            return r;
        }
        private Image Picture(string id, Transform parent, Vector2 anchor, Vector2 pos, Vector2 size, bool sliced = false)
        {
            var r = Rect(id, parent, anchor, pos, size); var image = r.gameObject.AddComponent<Image>();
            image.sprite = ArtCatalog.Sprite(id); image.raycastTarget = false;
            image.type = sliced ? Image.Type.Sliced : Image.Type.Simple;
            image.preserveAspect = !sliced;
            return image;
        }
        private Text Label(string text, Transform parent, Vector2 anchor, Vector2 pos, Vector2 size, int fontSize = 28)
        {
            var r = Rect("Text", parent, anchor, pos, size); var label = r.gameObject.AddComponent<Text>();
            label.font = font; label.fontSize = fontSize; label.text = text;
            label.color = new Color(.08f, .27f, .22f); label.alignment = TextAnchor.MiddleCenter;
            label.raycastTarget = false; return label;
        }
        private void Button(string label, Vector2 anchor, Vector2 pos, Vector2 size, UnityEngine.Events.UnityAction action)
        {
            var image = Picture("original-base__button_primary", page, anchor, pos, size, true);
            image.raycastTarget = true;
            var button = image.gameObject.AddComponent<Button>(); button.targetGraphic = image;
            button.onClick.AddListener(action);
            Label(label, image.transform, new Vector2(.5f, .5f), Vector2.zero, size - new Vector2(24, 10), 28);
        }
        private void NewPage(int newMode)
        {
            mode = newMode; controlled = null; drag = null; status = null;
            if (page != null) Destroy(page.gameObject);
            if (world != null) Destroy(world);
            page = Rect("Page", canvas.transform, new Vector2(.5f, .5f), Vector2.zero, Vector2.zero);
            page.anchorMin = Vector2.zero; page.anchorMax = Vector2.one; page.offsetMin = page.offsetMax = Vector2.zero;
            world = new GameObject("ArtWorld"); cameraView.transform.position = new Vector3(0, 0, -10);
            playing = true;
        }
        private void ShowMenu()
        {
            NewPage(0);
            Picture(portrait ? "original-base__bg_courtyard_portrait" : "original-base__bg_courtyard_landscape", page,
                new Vector2(.5f, .5f), Vector2.zero, scaler.referenceResolution);
            Picture("branding__yifu-zhen-wanyao-logo-primary", page, new Vector2(.5f, 1), new Vector2(0, -230), new Vector2(660, 440));
            Label("角色与动作接入预览", page, new Vector2(.5f, 1), new Vector2(0, -445), new Vector2(800, 70), 32);
            var heroes = new[] { "hero_daotong", "hero_lingyi", "hero_leixiu" };
            for (int i = 0; i < heroes.Length; i++)
            {
                string id = heroes[i]; var row = ArtCatalog.Actor(id);
                Vector2 pos = new Vector2((i - 1) * 330, -60);
                var card = Picture("original-base__panel_small", page, new Vector2(.5f, .5f), pos, new Vector2(306, 360), true);
                card.raycastTarget = true;
                var button = card.gameObject.AddComponent<Button>(); button.targetGraphic = card;
                button.onClick.AddListener(() => { selected = id; ShowMenu(); });
                Picture(row.staticArt, card.transform, new Vector2(.5f, .5f), new Vector2(0, 22), new Vector2(270, 270));
                Label(row.name + (selected == id ? " · 已选" : ""), card.transform, new Vector2(.5f, .5f), new Vector2(0, -132), new Vector2(290, 60), 28);
            }
            Button("进入移动场景", new Vector2(.5f, 0), new Vector2(-180, 150), new Vector2(310, 76), ShowMovement);
            Button("查看全部动作", new Vector2(.5f, 0), new Vector2(180, 150), new Vector2(310, 76), ShowAllActors);
            Label("本场景用于资源接入验收；战斗与业务逻辑尚未接入。", page, new Vector2(.5f, 0), new Vector2(0, 62), new Vector2(1000, 72), 24);
        }
        private ArtActor Spawn(string id, Vector2 position)
        {
            var prefab = Resources.Load<GameObject>("DaoActors/" + id);
            GameObject go = prefab != null ? Instantiate(prefab) : new GameObject(id, typeof(SpriteRenderer), typeof(ArtActor));
            go.name = id; go.transform.SetParent(world.transform, false); go.transform.position = position;
            var actor = go.GetComponent<ArtActor>(); actor.actorId = id; actor.playbackSpeed = slow ? .5f : 1;
            return actor;
        }
        private void Ground()
        {
            var quad = GameObject.CreatePrimitive(PrimitiveType.Quad); quad.name = "RepeatedGround";
            quad.transform.SetParent(world.transform, false); quad.transform.position = new Vector3(0, 0, 5);
            quad.transform.localScale = new Vector3(200, 200, 1);
            if (groundMaterial == null)
            {
                groundMaterial = new Material(Shader.Find("Unlit/Texture"));
                groundMaterial.mainTexture = ArtCatalog.Texture("env_battle_ground_01");
                groundMaterial.mainTextureScale = new Vector2(50, 50);
            }
            quad.GetComponent<MeshRenderer>().sharedMaterial = groundMaterial;
            Destroy(quad.GetComponent<Collider>());
        }
        private void Toolbar(string title)
        {
            var panel = Picture("original-base__panel_main", page, new Vector2(.5f, 1), new Vector2(0, -82), new Vector2(portrait ? 1050 : 1860, 148), true);
            Label(title, panel.transform, new Vector2(.5f, .5f), new Vector2(0, 26), new Vector2(1000, 60), 30);
            Button("返回", new Vector2(0, 1), new Vector2(105, -80), new Vector2(160, 68), ShowMenu);
            Button(slow ? "半速" : "正常速度", new Vector2(1, 1), new Vector2(-145, -80), new Vector2(230, 68), () =>
            {
                slow = !slow;
                foreach (var actor in world.GetComponentsInChildren<ArtActor>()) actor.playbackSpeed = slow ? .5f : 1;
                if (mode == 1) ShowAllActors(); else ShowMovement();
            });
        }
        private void ShowAllActors()
        {
            NewPage(1); Ground(); Toolbar("11个身份 · 四姿势行走／浮游循环");
            int cols = portrait ? 3 : 6;
            for (int i = 0; i < ArtCatalog.Data.actors.Length; i++)
            {
                var row = ArtCatalog.Data.actors[i]; int col = i % cols, line = i / cols;
                Vector2 pos = portrait ? new Vector2((col - 1) * 2, 3.5f - line * 2.6f) : new Vector2((col - 2.5f) * 3, 1.4f - line * 3.2f);
                Spawn(row.id, pos);
            }
            Label("检查身份、脚点、首尾恢复与真实透明边缘。", page, new Vector2(.5f, 0), new Vector2(0, 58), new Vector2(1000, 65), 26);
        }
        private void ShowMovement()
        {
            NewPage(2); Ground();
            var inputRect = Rect("DragMovement", page, new Vector2(.5f, .5f), Vector2.zero, Vector2.zero);
            inputRect.anchorMin = Vector2.zero; inputRect.anchorMax = Vector2.one; inputRect.offsetMin = inputRect.offsetMax = Vector2.zero;
            var hit = inputRect.gameObject.AddComponent<Image>(); hit.color = Color.clear; hit.raycastTarget = true;
            drag = inputRect.gameObject.AddComponent<PreviewDragInput>();
            controlled = Spawn(selected, Vector2.zero); controlled.walking = false;
            Toolbar("移动／停走／左右翻转与无限地面");
            status = Label("WASD／方向键移动；触屏按住场景拖动。ESC返回。", page, new Vector2(.5f, 0), new Vector2(0, 60), new Vector2(1000, 85), 26);
        }
        private void OnDestroy() { if (canvas != null) Destroy(canvas.gameObject); if (world != null) Destroy(world); if (groundMaterial != null) Destroy(groundMaterial); }
    }
}
