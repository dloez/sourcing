import { Plugin, App, Modal, type PluginManifest, TFile } from "obsidian"

import {
  SourcingClient,
  type SourcingUser,
  type SourcingASPSPSource,
  type SourcingCryptowalletSource,
} from "./sourcing"

const client = new SourcingClient()

export default class SourcingObsidianPlugin extends Plugin {
  access_token: string
  refresh_token: string

  constructor(app: App, manifest: PluginManifest) {
    super(app, manifest)
    this.access_token = ""
    this.refresh_token = ""
  }

  async onload(): Promise<void> {
    this.addCommand({
      id: "login",
      name: "Login into Sourcing",
      callback: () => {
        new LoginModal(this.app, this).open()
      },
    })

    const data = await this.loadData()
    if (
      !data.hasOwnProperty("access_token") ||
      !data.hasOwnProperty("refresh_token")
    ) {
      return
    }

    const credentials = await verifyCredentials(
      data.access_token,
      data.refresh_token
    )
    this.access_token = credentials.access_token
    this.refresh_token = credentials.refresh_token

    if (!this.access_token) {
      return
    }
    this.saveData(credentials)

    await this.setupVault()
    const userData: SourcingUser = await client.me(this.access_token)
    userData.sources.forEach((source) => {
      if (source.kind === "aspsp") {
        this.updateASPSPSourceData(source)
      } else if (source.kind === "crypto_wallet") {
        this.updateCryptowalletSourceData(source)
      }
    })
  }

  async setupVault() {
    if (this.app.vault.getAbstractFileByPath("sourcing")) {
      return
    }
    await this.app.vault.createFolder("sourcing")
  }

  async updateASPSPSourceData(source: SourcingASPSPSource) {
    let fileName = source.details.name + ".md"
    let data = ""
    data += `- Currency: ${source.details.currency}\n`
    data += `- Balance: ${source.latest_balances[0].amount}\n`

    const filePath = "sourcing/" + fileName
    const file = this.app.vault.getAbstractFileByPath(filePath)

    if (file instanceof TFile) {
      await this.app.vault.modify(file, data)
    } else {
      await this.app.vault.create(filePath, data)
    }
  }

  async updateCryptowalletSourceData(source: SourcingCryptowalletSource) {
    let fileName = source.details.wallet_address + ".md"
    let data = ""
    data += `- Wallet Address: ${source.details.wallet_address}\n`
    data += `- Coin: ${source.details.coin.symbol}\n`
    data += `- Balance: ${source.latest_balances[0].amount}\n`

    const filePath = "sourcing/" + fileName
    const file = this.app.vault.getAbstractFileByPath(filePath)

    if (file instanceof TFile) {
      await this.app.vault.modify(file, data)
    } else {
      await this.app.vault.create(filePath, data)
    }
  }
}

async function verifyCredentials(
  access_token: string,
  refresh_token: string
): Promise<{ access_token: string; refresh_token: string }> {
  const { expires_in: access_token_expires_in } = await client.verifyToken(
    access_token
  )
  if (access_token_expires_in) {
    return { access_token, refresh_token }
  }

  const { expires_in: refresh_token_expires_in } = await client.verifyToken(
    refresh_token
  )

  if (refresh_token_expires_in) {
    const response = await client.refreshToken(refresh_token)
    return {
      access_token: response.access_token,
      refresh_token: response.refresh_token,
    }
  }

  return { access_token: "", refresh_token: "" }
}

class LoginModal extends Modal {
  plugin: SourcingObsidianPlugin

  constructor(app: App, plugin: SourcingObsidianPlugin) {
    super(app)
    this.plugin = plugin
  }

  async onOpen() {
    const { contentEl } = this
    contentEl.createEl("h2", { text: "Login" })
    const form = contentEl.createEl("form")
    form.createEl("label", { text: "Username:" }).createEl("input", {
      attr: { type: "text", id: "username" },
    })
    form.createEl("label", { text: "Password:" }).createEl("input", {
      attr: { type: "password", id: "password" },
    })
    form
      .createEl("button", { text: "Submit" })
      .addEventListener("click", async (event) => {
        event.preventDefault()
        const username = (form.querySelector("#username") as HTMLInputElement)
          .value
        const password = (form.querySelector("#password") as HTMLInputElement)
          .value

        const { access_token, refresh_token } = await client.getToken(
          username,
          password
        )
        await this.plugin.saveData({ access_token, refresh_token })
      })
  }

  onClose() {
    const { contentEl } = this
    contentEl.empty()
  }
}
