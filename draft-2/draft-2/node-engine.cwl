{
    class: ExpressionEngineRequirement,
    requirements: [
      {
        class: DockerRequirement,
        dockerImageId: commonworkflowlanguage/nodejs-engine
      }
    ],
    engineCommand: cwlNodeEngine.js
}
