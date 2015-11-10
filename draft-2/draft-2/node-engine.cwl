{
    class: ExpressionEngineRequirement,
    requirements: [
      {
        class: DockerRequirement,
        dockerPull: commonworkflowlanguage/nodejs-engine
      }
    ],
    engineCommand: cwlNodeEngine.js
}
