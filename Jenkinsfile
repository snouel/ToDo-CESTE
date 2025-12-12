pipeline {

    agent any
     // <--- 
    // PARÁMETROS DE EJECUCIÓN
    // ************************************************
    parameters {
        string(name: 'PARAM_DOCKER_VERSION', defaultValue: '1.0.0', description: 'Etiqueta de versión para la Imagen Docker.')
        booleanParam(name: 'PARAM_BUILD_IMAGE', defaultValue: true, description: 'Marcar si se debe construir la Imagen Docker después de pasar las pruebas.')
        booleanParam(name: 'PARAM_PUSH_IMAGE', defaultValue: true, description: 'Marcar si la imagen construida debe subirse a DockerHub.')
    }

    // ************************************************
    // VARIABLES DE ENTORNO Y CREDENCIALES
    // ************************************************
    environment {
        DOCKERHUB_CREDENTIALS_ID = 'docker-hub-credentials'
        DOCKERHUB_REPO = 'devsnouel/todo-ceste'
        SONAR_AUTH_TOKEN_ID = 'sonar-auth-token-id' 
        SONAR_PROJECT_KEY = 'todo-ceste'
    }

    stages {
        // ETAPA 1: CLONAR CÓDIGO
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // ETAPA 2: INSTALACIÓN DE DEPENDENCIAS Y PRUEBAS (CI)
        stage ('Install & Tests (pip)') {
            steps {
                // 1. Instala dependencias
                bat 'python -m pip install -r requirements.txt' 
                
                // 2. NUEVO: VALIDACIÓN NATIVA DE SINTAXIS (SIN FLAKE8)
                // Ejecuta el script que usa py_compile para revisar todos los archivos.
                bat 'python syntax_check.py'

                // 3. Ejecuta Pytest como un módulo de Python
                // Esto le dice a Python que ejecute el módulo 'pytest'
                bat 'python -m pytest test_logic.py'
            }
        }

        // ETAPA 3: ANÁLISIS DE CÓDIGO (SONARQUBE)
        stage ('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: SONAR_AUTH_TOKEN_ID, variable: 'SONAR_TOKEN')]) {
                    withSonarQubeEnv('SonarQube-Server') { 
                        bat  """
                            sonnar-scanner ^
                                -Dsonar.projectKey=todo-ceste ^
                                -Dsonar.sources=. ^
                                -Dsonar.host.url=http://localhost:9000
                                -Dsonar.login=%SONAR_TOKEN% ^
                                -Dsonar.qualitygate.wait=true
                        """
                    }
                }
            }
        }

        // ETAPA 4: CONSTRUCCIÓN DE LA IMAGEN DOCKER (CD)
        stage('Build Docker Image') {
            when { expression { return params.PARAM_BUILD_IMAGE } } 
            steps {
                script {
                    def dockerImageTag = params.PARAM_DOCKER_VERSION
                    img = docker.build("${DOCKERHUB_REPO}:${dockerImageTag}", "-f Dockerfile .")
                }
            }
        }

         // ETAPA 5: ANÁLISIS DE VULNERABILIDADES (TRIVY)
        stage('Image Security Scan (Trivy)') {
                when { expression { return params.PARAM_BUILD_IMAGE } } // Solo si se construyó la imagen
                // ... dentro de la etapa 'Image Security Scan (Trivy)'

                steps {
                    script {
                        def dockerImageTag = params.PARAM_DOCKER_VERSION
                        def fullImageName = "${DOCKERHUB_REPO}:${dockerImageTag}"
                        
                        // Comando CORREGIDO: Uso de comillas triples (""") y eliminación del ^
                        bat """
                            docker run --rm \\
                                -v //var/run/docker.sock:/var/run/docker.sock \\
                                aquasec/trivy:latest image \\
                                --severity CRITICAL,HIGH \\
                                --exit-code 1 \\
                                --ignore-unfixed %fullImageName%
                        """
                }
            }
        }
        

        // ETAPA 6: PUBLICACIÓN EN DOCKERHUB (CD)
        stage('Push to DockerHub') {
            when { expression { return params.PARAM_PUSH_IMAGE && params.PARAM_BUILD_IMAGE } } 
            steps {
                script {
                    def dockerImageTag = params.PARAM_DOCKER_VERSION

                    withCredentials([usernamePassword(
                        credentialsId: DOCKERHUB_CREDENTIALS_ID,
                        passwordVariable: 'DOCKER_TOKEN', 
                        usernameVariable: 'DOCKER_USERNAME' 
                    )]) {
                        
                        powershell "echo $env:DOCKER_TOKEN | docker login -u $env:DOCKER_USERNAME --password-stdin"
                        
                        bat "docker push ${DOCKERHUB_REPO}:${dockerImageTag}"
                        bat "docker push ${DOCKERHUB_REPO}:latest"
                    }
                }
            }
        }
    }
}
