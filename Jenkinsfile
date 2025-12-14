//-- Jekinsfile v1 --

def isDockerHubLoggedOn = false

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
        SONAR_AUTH_TOKEN_ID = 'sonar-auth-token' 
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
            environment {
                SONAR_HOST_URL = 'http://host.docker.internal:9000'
            }
            
            steps {
                withCredentials([string(credentialsId: SONAR_AUTH_TOKEN_ID, variable: 'SONAR_TOKEN')]) {
                    
                    echo "--- Cleaning Caches & Running SonarQube ---"
                    
                    // 1. LIMPIEZA PREVIA: Borramos las carpetas que bloquean por permisos.
                    // Usamos 'if exist' para que no falle si la carpeta no existe.
                    bat "if exist .pytest_cache rd /s /q .pytest_cache"
                    bat "if exist __pycache__ rd /s /q __pycache__"
                    
                    // 2. EJECUCIÓN DEL ESCÁNER
                    // Nota: Ya no es estrictamente necesario excluirlas en el comando si las borramos,
                    // pero dejamos la exclusión por seguridad.
                    bat """
                        docker run --rm -v "%CD%":/usr/src sonarsource/sonar-scanner-cli:latest ^
                        -Dsonar.projectKey=todo-ceste ^
                        -Dsonar.sources=. ^
                        -Dsonar.exclusions=syntax_check.py,tasks.py,**/.pytest_cache/**/*,**/__pycache__/**/* ^
                        -Dsonar.login=%SONAR_TOKEN% ^
                        -Dsonar.host.url=%SONAR_HOST_URL% ^
                        -Dsonar.qualitygate.wait=true
                    """
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

        // ETAPA 5: ESCANEO DE SEGURIDAD (TRIVY)
        stage ('Image Security Scan (Trivy)') {
            when { expression { return params.PARAM_BUILD_IMAGE } } 
            steps {
                script {
                    def dockerImageTag = params.PARAM_DOCKER_VERSION
                    // Asegúrate de que esta variable coincida con como la definiste antes (REPO:TAG)
                    def fullImageName = "${DOCKERHUB_REPO}:${dockerImageTag}"
                    
                    echo "--- Scanning Image: ${fullImageName} ---"
                    
                    // CORRECCIÓN: Comando en UNA SOLA LÍNEA para evitar errores de sintaxis en Windows.
                    // Usamos %fullImageName% si es una variable de entorno, o interpolación de Groovy ${fullImageName}
                    // Aquí usaremos la interpolación directa de Groovy que es más segura dentro de comillas dobles.
                    bat "docker run --rm -v //var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --severity CRITICAL,HIGH --exit-code 1 --ignore-unfixed ${fullImageName}"
                }
            }
        }


        // ETAPA 6: PUBLICACIÓN EN DOCKERHUB (CD)
        stage('Push to DockerHub') {
            when { expression { return params.PARAM_PUSH_IMAGE && params.PARAM_BUILD_IMAGE } } 
            steps {
                script {

                    def dockerImageTag = params.PARAM_DOCKER_VERSION

                    withCredentials([usernamePassword(credentialsId: DOCKERHUB_CREDENTIALS_ID, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        
                        bat "echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin"
                        
                        bat "docker push ${DOCKERHUB_REPO}:${params.PARAM_DOCKER_VERSION}"
                        bat "docker tag ${DOCKERHUB_REPO}:${params.PARAM_DOCKER_VERSION} ${DOCKERHUB_REPO}:latest"
                        bat "docker push ${DOCKERHUB_REPO}:latest"
                    }

                    isDockerHubLoggedOn = true

                }
            }
        }

        // ETAPA 7: DESPLIEGUE LOCAL (Deploy)
        stage ('Deploy to Local Docker') {
            when { expression {params.PARAM_BUILD_IMAGE } }
            steps {
                script {
                    def dockerImageTag = params.PARAM_DOCKER_VERSION
                    def fullImageName = "${DOCKERHUB_REPO}:${dockerImageTag}"
                    
                    // 1. Detener y borrar el contenedor anterior (si existe) para evitar conflictos de nombre/puerto
                    // Usamos try/catch o ignoramos errores por si es la primera vez y no existe.
                    bat "docker stop todo-fastapi || exit 0"
                    bat "docker rm todo-fastapi || exit 0"
                    
                    // 2. Correr el nuevo contenedor mapeando el puerto 8000
                    echo "--- Deploying Container: ${fullImageName} ---"
                    bat "docker run -d -p 8000:8000 --name todo-fastapi ${fullImageName}"
                }
            }
        }
    }

    post {
            // 1. ALWAYS: Se ejecuta SIEMPRE (pase lo que pase)
            always {
                script {
                    if (isDockerHubLoggedOn){
                    echo '--- Cerrando sesión de DockerHub (Logout) ---'                    
                    bat "docker logout"
                    }else {
                    echo '--- No se requiere Logout (No se hizo Push) ---'
                    }

                }
                
                echo '--- Limpiando Docker y Cerrando Sesión ---'
                // Borra imágenes huerfanas (<none>)
                bat "docker system prune -f"
                // Cierra sesión en DockerHub por seguridad
            }

            // 2. SUCCESS: Solo si todo salió VERDE
            success {
                echo '¡El despliegue fue exitoso! La API está online.'
            }

            // 3. FAILURE: Solo si algo FALLÓ (Rojo)
            failure {
                echo 'Algo salió mal. Revisar los logs.'
            }

            // 4. CLEANUP: Se ejecuta al final de todo
            cleanup {
                echo '--- Borrando archivos del Workspace ---'
                cleanWs()
            }
        }
}
