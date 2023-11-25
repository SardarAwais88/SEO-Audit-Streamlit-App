import streamlit as st
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

def generate_seo_audit_report(url):
    result = {"success": False, "message": "", "result": {}}

    try:
        # Fetch the webpage content
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Generate the SEO audit report
        result["success"] = True
        result["message"] = "Report Generated Successfully"
        result["result"]["Input"] = {"URL": url, "Input type": "Domain"}

        # HTTP section
        result["result"]["http"] = {
            "status": response.status_code,
            "using_https": url.startswith("https"),
            "contentSize": {
                "bytes": len(response.content),
                "kb": len(response.content) / 1024
            },
            "headers": dict(response.headers),
            "redirections": len(response.history) > 0,
            "responseTime": f"{response.elapsed.total_seconds():.5f} seconds"
        }

        # Title section
        result["result"]["title"] = {
            "found": "Found",
            "data": soup.title.string.strip() if soup.title else "",
            "length": len(soup.title.string.strip()),
            "characters": len(soup.title.string.strip()),
            "words": len(soup.title.string.strip().split()),
            "charPerWord": len(soup.title.string.strip()) / len(soup.title.string.strip().split()),
            "tag number": len(soup.find_all('title'))
        }

        # Meta Description section
        meta_description_tag = soup.find('meta', attrs={'name': 'description'})
        result["result"]["meta_description"] = {
            "found": "Found" if meta_description_tag else "Not Found",
            "data": meta_description_tag.get('content').strip() if meta_description_tag else "",
            "length": len(meta_description_tag.get('content').strip()) if meta_description_tag else 0,
            "characters": len(meta_description_tag.get('content').strip()) if meta_description_tag else 0,
            "words": len(meta_description_tag.get('content').strip().split()) if meta_description_tag else 0,
            "charPerWord": len(meta_description_tag.get('content').strip()) / len(meta_description_tag.get('content').strip().split()) if meta_description_tag else 0,
            "number": 1 if meta_description_tag else 0
        }

        # Metadata Info section
        result["result"]["metadata_info"] = {
            "charset": response.encoding,
            "canonical": soup.find('link', {'rel': 'canonical'}).get('href') if soup.find('link', {'rel': 'canonical'}) else "",
            "favicon": soup.find('link', {'rel': 'icon'}).get('href') if soup.find('link', {'rel': 'icon'}) else "",
            "viewport": soup.find('meta', {'name': 'viewport'}).get('content') if soup.find('meta', {'name': 'viewport'}) else "",
            # Add other metadata info as needed
        }

        # Page Headings Summary section
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        heading_counts = {f'H{i}': headings.count(f'H{i}') for i in range(1, 7)}
        result["result"]["Page Headings summary"] = {
            **heading_counts,
            "H1 count": heading_counts.get('H1', 0),
            "H1 Content": headings[0].text.strip() if heading_counts.get('H1', 0) > 0 else ""
        }

        # Word Count section
        text_content = soup.get_text()
        words = text_content.split()
        result["result"]["word_count"] = {
            "total": len(words),
            "Corrected word count": len(words),
            "Anchor text words": 0,  # Add logic to calculate anchor text words
            "Anchor Percentage": 0  # Add logic to calculate anchor text percentage
        }

        # Links Summary section
        links = soup.find_all('a')
        link_list = [{"href": link.get('href'), "text": link.text.strip()} for link in links]
        result["result"]["links_summary"] = {
            "Total links": len(links),
            "External links": sum('http' in link.get('href') for link in links),
            "Internal": sum('http' not in link.get('href') for link in links),
            "Nofollow count": sum('nofollow' in str(link) for link in soup.find_all('a', rel='nofollow')),
            "links": link_list
        }

        # Images Analysis section
        images = soup.find_all('img')
        image_list = [{"src": image.get('src'), "alt": image.get('alt')} for image in images]
        result["result"]["images_analysis"] = {
            "summary": {
                "total": len(images),
                "No src tag": sum('src' not in image.attrs for image in images),
                "No alt tag": sum('alt' not in image.attrs for image in images)
            },
            "data": image_list
        }

    except requests.RequestException as e:
        result["message"] = f"Error fetching URL: {str(e)}"

    return result

def run_audit(url):
    try:
        audit_result = generate_seo_audit_report(url)
        return audit_result
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "result": {}}

def main():
    st.title("SEO Audit Tool")

    # User input for URL
    url = st.text_input("Enter URL:")

    # Button to trigger SEO audit
    if st.button("Audit"):
        if not urlparse(url).scheme or not urlparse(url).netloc:
            st.warning("Please enter a valid URL.")
        else:
            # Run the audit and display the result
            audit_result = run_audit(url)
            display_result(audit_result)

def display_result(audit_result):
    # Display the audit result in the Streamlit app
    st.header("Audit Result")
    st.json(audit_result)

# Run the Streamlit app
if __name__ == "__main__":
    main()
