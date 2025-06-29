my_node = k8sagent(name: 'python3.12.0+sonarscan')
podTemplate(my_node) {
  node(my_node.label) {
        env.PROJECT_NAME = "ocr-detection-recognition"
        env.SERVICE_NAME = "ocr-detection-recognition"
        newkyc_common()
    }
}