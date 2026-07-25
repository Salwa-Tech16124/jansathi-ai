import json
import urllib.request
import urllib.error
import logging
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger("jansathi.sarvam")


class SarvamAIService:
    """
    Dedicated Client Service for Sarvam AI Reasoning API.
    Handles authentication, payload formatting, network timeouts, and HTTP error recovery.
    """

    @property
    def api_key(self) -> Optional[str]:
        return settings.SARVAM_API_KEY

    @property
    def base_url(self) -> str:
        return settings.SARVAM_BASE_URL.rstrip('/')

    @property
    def model(self) -> str:
        return settings.SARVAM_MODEL

    def is_configured(self) -> bool:
        """Check if Sarvam API key is configured."""
        key = self.api_key
        return bool(key and key.strip())

    def completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.2, 
        max_tokens: int = 1000
    ) -> Optional[str]:
        """
        Execute chat completion request against Sarvam AI API.
        
        Returns raw text string or None on failure/timeout/invalid key.
        """
        if not self.is_configured():
            logger.warning("[SARVAM AI] API key not configured (SARVAM_API_KEY is empty).")
            return None

        url = f"{self.base_url}/v1/chat/completions"
        active_key = self.api_key.strip()
        headers = {
            "Content-Type": "application/json",
            "api-subscription-key": active_key,
            "Authorization": f"Bearer {active_key}"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            req_data = json.dumps(payload).encode('utf-8')
            request = urllib.request.Request(url, data=req_data, headers=headers, method="POST")

            with urllib.request.urlopen(request, timeout=10.0) as response:
                if response.status == 200:
                    body = response.read().decode('utf-8')
                    data = json.loads(body)

                    if "choices" in data and len(data["choices"]) > 0:
                        choice = data["choices"][0]
                        if "message" in choice and "content" in choice["message"]:
                            return choice["message"]["content"]
                        elif "text" in choice:
                            return choice["text"]
                    
                    logger.warning("[SARVAM AI] Response payload missing expected choices format.")
                    return None
                else:
                    logger.error(f"[SARVAM AI] HTTP Status {response.status}")
                    return None

        except urllib.error.HTTPError as http_err:
            if http_err.code == 401:
                logger.error("[SARVAM AI Error] 401 Unauthorized - Invalid or expired SARVAM_API_KEY.")
            elif http_err.code == 429:
                logger.error("[SARVAM AI Error] 429 Rate Limit Exceeded.")
            else:
                logger.error(f"[SARVAM AI Error] HTTP {http_err.code}: {http_err.reason}")
            return None

        except urllib.error.URLError as url_err:
            logger.error(f"[SARVAM AI Error] Network error / Timeout: {url_err.reason}")
            return None

        except Exception as err:
            logger.error(f"[SARVAM AI Error] Unexpected error during request: {err}")
            return None

    def transcribe_audio_url(self, audio_url: str) -> Optional[str]:
        """
        Download voice note audio from URL and transcribe via Sarvam AI Speech-to-Text (Saaras v3).
        """
        if not self.is_configured() or not audio_url:
            return None

        try:
            # Download audio file from Twilio / public media URL
            req = urllib.request.Request(audio_url, headers={"User-Agent": "JanSathiAI/1.0"})
            with urllib.request.urlopen(req, timeout=12.0) as resp:
                audio_bytes = resp.read()

            if not audio_bytes:
                return None

            # Execute multipart/form-data request to Sarvam Speech-to-Text
            url = f"{self.base_url}/speech-to-text"
            boundary = "----JanSathiFormBoundaryVoiceSTT"
            
            body = []
            body.append(f"--{boundary}\r\n".encode('utf-8'))
            body.append(b'Content-Disposition: form-data; name="model"\r\n\r\n')
            body.append(b'saaras:v3\r\n')
            body.append(f"--{boundary}\r\n".encode('utf-8'))
            body.append(b'Content-Disposition: form-data; name="file"; filename="voice.ogg"\r\nContent-Type: audio/ogg\r\n\r\n')
            body.append(audio_bytes)
            body.append(b'\r\n')
            body.append(f"--{boundary}--\r\n".encode('utf-8'))
            
            payload = b"".join(body)
            active_key = self.api_key.strip()
            headers = {
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "api-subscription-key": active_key,
                "Authorization": f"Bearer {active_key}"
            }

            stt_req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(stt_req, timeout=15.0) as stt_resp:
                if stt_resp.status == 200:
                    result_json = json.loads(stt_resp.read().decode('utf-8'))
                    transcript = result_json.get("transcript") or result_json.get("text", "")
                    if transcript:
                        logger.info(f"[Sarvam STT] Successfully transcribed voice note: '{transcript}'")
                        return transcript.strip()

        except Exception as err:
            logger.warning(f"[Sarvam STT Warning] Voice note transcription notice: {err}")
            return None

        return None


# Singleton Sarvam AI Service instance
sarvam_client = SarvamAIService()
