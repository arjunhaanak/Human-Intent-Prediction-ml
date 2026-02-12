try:
    from moviepy import VideoFileClip
    print("Import successful from moviepy")
except ImportError:
    try:
        from moviepy.editor import VideoFileClip
        print("Import successful from moviepy.editor")
    except ImportError as e:
        print(f"Import failed: {e}")
