{
    class: ExpressionEngineRequirement,
    id: "#js",
    requirements: [
      {
        class: DockerRequirement,
        dockerImageId: cwl-nodejs-engine
      }
    ],
    engineCommand: cwlNodeEngine.js
}
