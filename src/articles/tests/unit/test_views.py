import pytest
from django.urls import reverse
from pyquery import PyQuery as pq

TIMESPAN = 7  # no. of days


#
# Test IndexView
#
@pytest.mark.django_db
def test_index_view(client, source_instance, article_instance) -> None:
    response = client.get(reverse("index"))

    assert response.status_code == 200

    html = response.content.decode("utf-8")
    doc = pq(html)

    # assert that details of source are present in response content
    source_title = doc.find(".source-title").text()
    source_link = doc.find(".source-link")
    source_link_href = source_link.attr("href")

    assert source_title == source_instance.title
    assert source_link.is_("a")
    assert source_link_href == source_instance.url

    # assert that details of article are present in response content
    article_title = doc.find(".article-headline").text()
    article_link = doc.find(".article-link")
    article_link_href = article_link.attr("href")
    article_link_title = article_link.attr("title")

    assert article_title == article_instance.title
    assert article_link.is_("a")
    assert article_link_href == article_instance.url
    assert article_instance.title in article_link_title


#
# Test SearchResultsView
#
@pytest.mark.django_db
def test_search_results_view(
    client,
    source_instance,
    source_instance_2,
    article_values,
    article_instance,
    article_instance_2,
) -> None:
    query_params = {"q": article_values["title"][:5]}
    response = client.get(reverse("search"), query_params)
    html = response.content.decode("utf-8")
    doc = pq(html)

    assert response.status_code == 200

    # assert that details of source matching query are present in response content
    source_title = doc.find(".source-title").text()
    source_link = doc.find(".source-link")
    source_link_href = source_link.attr("href")

    assert source_title == source_instance.title
    assert source_link.is_("a")
    assert source_link_href == source_instance.url

    # assert that details of article matching query are present in response content
    article_title = doc.find(".article-headline").text()
    article_link = doc.find(".article-link")
    article_link_href = article_link.attr("href")
    article_link_title = article_link.attr("title")

    assert article_title == article_instance.title
    assert article_link.is_("a")
    assert article_link_href == article_instance.url
    assert article_instance.title in article_link_title
    assert article_instance.title in article_link_title

    # assert that details of non-matching source are not found
    assert source_instance_2.title not in html
    assert source_instance_2.url not in html

    # assert that details of non-matching article are not found
    assert article_instance_2.title not in html
    assert article_instance_2.url not in html
    assert article_instance_2.title not in html


@pytest.mark.django_db
def test_search_result_not_found(
    client,
    source_instance,
    source_instance_2,
    article_instance,
    article_instance_2,
) -> None:
    query_params = {"q": "test"}
    response = client.get(reverse("search"), query_params)
    html = response.content.decode("utf-8")

    assert response.status_code == 200

    # assert that details of non-matching source are not found
    assert source_instance.title not in html
    assert source_instance.url not in html

    # assert that details of non-matching article are not found
    assert article_instance.title not in html
    assert article_instance.url not in html
    assert article_instance.title not in html


@pytest.mark.django_db
def test_search_result_substring(
    client,
    source_instance,
    article_instance,
    article_values,
) -> None:
    query_params = {"q": article_values["title"][2:7]}
    response = client.get(reverse("search"), query_params)
    html = response.content.decode("utf-8")

    assert response.status_code == 200

    # assert that details of non-matching source are not found
    assert source_instance.title not in html
    assert source_instance.url not in html

    # assert that details of non-matching article are not found
    assert article_instance.title not in html
    assert article_instance.url not in html
    assert article_instance.title not in html
