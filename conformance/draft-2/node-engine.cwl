{
    class: ExpressionEngineRequirement,
    requirements: [
      {
        class: DockerRequirement,
        dockerImageId: cwl-nodejs-engine
      }
    ],
    engineCommand: cwlNodeEngine.js
}
