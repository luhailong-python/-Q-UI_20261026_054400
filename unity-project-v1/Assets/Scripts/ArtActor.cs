using UnityEngine;

namespace YifuArt
{
    [RequireComponent(typeof(SpriteRenderer))]
    public sealed class ArtActor : MonoBehaviour
    {
        public string actorId = "hero_daotong";
        public bool walking = true;
        public float playbackSpeed = 1;
        private SpriteRenderer view;
        private Animator animator;
        private ActorRow row;
        private Sprite[] frames;
        private float clock;
        private bool ready;
        private void Start() { EnsureReady(); }
        private void EnsureReady()
        {
            if (ready) return;
            row = ArtCatalog.Actor(actorId);
            view = GetComponent<SpriteRenderer>();
            animator = GetComponent<Animator>();
            frames = new Sprite[row.frames.Length];
            for (int i = 0; i < frames.Length; i++) frames[i] = ArtCatalog.Sprite(row.frames[i]);
            view.sprite = frames[0];
            float height = row.staticVisibleHeightPx / 128f;
            transform.localScale = Vector3.one * row.displayHeight / Mathf.Max(height, .01f);
            ready = true;
        }
        public void Move(Vector2 delta)
        {
            EnsureReady();
            walking = delta.sqrMagnitude > .0001f;
            if (Mathf.Abs(delta.x) > .001f) view.flipX = delta.x < 0;
            transform.position += (Vector3)delta;
        }
        private void Update()
        {
            EnsureReady();
            view.sortingOrder = 1000 - Mathf.RoundToInt(transform.position.y * 100);
            if (animator != null && animator.runtimeAnimatorController != null)
            {
                animator.SetBool("Walking", walking);
                animator.speed = playbackSpeed;
                return;
            }
            if (!walking) { clock = 0; view.sprite = frames[0]; return; }
            float duration = 0;
            foreach (float seconds in row.seconds) duration += seconds;
            clock = (clock + Time.deltaTime * playbackSpeed) % duration;
            float cursor = clock;
            for (int i = 0; i < frames.Length; i++)
            {
                cursor -= row.seconds[i];
                if (cursor < 0) { view.sprite = frames[i]; break; }
            }
        }
    }
}
