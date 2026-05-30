def safe_import(module_name):
    try:
        return __import__(module_name)
    except Exception as e:
        print(f"[lazy_imports] WARNING: Failed to import {module_name}: {e}")
        return None

chromadb = safe_import("chromadb")
llama_index = safe_import("llama_index")
onnxruntime = safe_import("onnxruntime")
celery = safe_import("celery")
kubernetes = safe_import("kubernetes")
