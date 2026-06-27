// Auto-generated Rust SDK for Preflight Designer
use reqwest::header::{HeaderMap, HeaderValue, AUTHORIZATION};
use serde_json::json;

pub struct ShinyFishstickSiteSDK {
    root_url: String,
    client: reqwest::blocking::Client,
    session_token: Option<String>,
}

impl ShinyFishstickSiteSDK {
    pub fn new(root_url: &str) -> Self {
        Self {
            root_url: root_url.to_string(),
            client: reqwest::blocking::Client::new(),
            session_token: None,
        }
    }

    pub fn login(&mut self, email: &str, password: &str) -> Result<(), Box<dyn std::error::Error>> {
        // Browser Action: login
        // Selector: #login-form
        println!("Interacting with element #login-form...");
        Ok(())
    }
    pub fn search_products(&mut self, q: &str) -> Result<(), Box<dyn std::error::Error>> {
        // Browser Action: search_products
        // Selector: #search-form
        println!("Interacting with element #search-form...");
        Ok(())
    }
    pub fn checkout(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        // Browser Action: checkout
        // Selector: #checkout-submit-btn
        println!("Interacting with element #checkout-submit-btn...");
        Ok(())
    }
    pub fn add_to_cart(&mut self, product_id: &str, quantity: i64) -> Result<(), Box<dyn std::error::Error>> {
        let url = format!("{}/{}", self.root_url, "api/cart/add");
        let body = json!({"product_id": product_id, "quantity": quantity});
        let mut req = self.client.post(&url);
        if let Some(ref token) = self.session_token {
            req = req.header(AUTHORIZATION, format!("Bearer {}", token));
        }
        let res = req.json(&body).send()?;
        Ok(())
    }
}
