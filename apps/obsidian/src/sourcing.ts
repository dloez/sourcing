const BASE_URL = "http://localhost:8000"

interface TokenData {
  access_token?: string
  refresh_token?: string
}

interface SourcingUser {
  id: string
  name: string
  email: string
  sources: Array<SourcingASPSPSource | SourcingCryptowalletSource>
}

interface SourcingASPSPSource {
  kind: "aspsp"
  details: {
    currency: string
    iban: string | null
    name: string
  }
  latest_balances: Array<SourcingBalance>
}

interface SourcingCryptowalletSource {
  kind: "crypto_wallet"
  details: {
    coin: {
      symbol: string
    }
    wallet_address: string
  }
  latest_balances: Array<SourcingBalance>
}

interface SourcingBalance {
  amount: number
  date: string
  name: string
}

class SourcingClient {
  async getToken(
    username: string,
    password: string
  ): Promise<{ access_token: string; refresh_token: string }> {
    const response = await postData(`${BASE_URL}/token`, {
      username,
      password,
      grant_type: "password",
    })

    return {
      access_token: response.access_token,
      refresh_token: response.refresh_token,
    }
  }

  async refreshToken(
    refresh_token: string
  ): Promise<{ access_token: string; refresh_token: string }> {
    const response = await postData(`${BASE_URL}/token`, {
      refresh_token,
      grant_type: "refresh_token",
    })

    return {
      access_token: response.access_token,
      refresh_token: response.refresh_token,
    }
  }

  async verifyToken(
    access_token?: string,
    refresh_token?: string
  ): Promise<{ expires_in: string }> {
    const data: TokenData = {}

    if (access_token) {
      data.access_token = access_token
    }

    if (refresh_token) {
      data.refresh_token = refresh_token
    }

    const response = await postData(`${BASE_URL}/token/verify`, data)
    return { expires_in: response.expires_in }
  }

  async me(access_token: string) {
    return getData(`${BASE_URL}/users/me`, {
      Authorization: `Bearer ${access_token}`,
    })
  }
}

async function postData(url = "", data = {}, headers = {}) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    body: JSON.stringify(data),
  })

  return response.json()
}

async function getData(url = "", headers = {}) {
  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
  })

  return response.json()
}

export { SourcingClient }
export type { SourcingUser, SourcingASPSPSource, SourcingCryptowalletSource }
