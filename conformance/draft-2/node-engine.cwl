{
    class: ExpressionEngineRequirement,
    id: "#js",
    requirements: [
      {
        class: DockerRequirement,
        dockerImageId: commonworkflowlanguage/nodejs-engine
      }
    ],
    engineCommand: cwlNodeEngine.js
}
