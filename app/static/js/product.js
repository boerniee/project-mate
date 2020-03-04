class ProductCard extends HTMLElement {
  constructor() {
    super();
    this.addEventListener("click", e => this.consume(e));
  }

  show_modal(title, body) {
    var modal = $('#resultmodal');
    modal.find('.modal-body').text(body);
    modal.find('.modal-header h4').html(title);
    modal.modal('toggle');
  }

  connectedCallback() {
    this.renderDom();
    this.fetchOffer();
  }

  consume(event) {
    if (this.disabled || this.offerid == null) return
    this.fetchOffer();
    $.post({
      url: "/ajax/consume/offer/id".replace('id', this.offerid),
      context: this,
      success: function(data) {
        this.show_modal(data['title'], data['text']);
        this.fetchOffer();
      },
      fail: function() {
        alert("fehler");
      }
    });
  }

  set stock(stock) {
    this.shadowRoot.getElementById('stock').innerHTML = " " + stock;
  }

  set price(price) {
    this.shadowRoot.getElementById('price').innerHTML = " " + price;
  }

  set supplier(supplier) {
    var supplierElement = this.shadowRoot.getElementById('supplier');
    var supplierIcon = document.createElement('i');
    supplierIcon.setAttribute('class', 'fas fa-people-carry');
    supplierElement.innerHTML = "";
    supplierElement.appendChild(supplierIcon);
    supplierElement.innerHTML = supplierElement.innerHTML + " " + supplier;
    supplierElement.setAttribute('title', supplier);
  }

  get disabled() {
    return this.hasAttribute('disabled');
  }

  set disabled(val) {
    if (val) {
      this.setAttribute('disabled', '');
    } else {
      this.removeAttribute('disabled');
    }
  }

  get productId() {
    return this.getAttribute('productid')
  }

  set badge(text) {
    if (this.getAttribute('badge') === text) return;
    var badge = this.shadowRoot.getElementById("badge")
    if (badge) {
      badge.remove();
    }
    var badge = document.createElement('div');
    badge.setAttribute('id', 'badge');
    badge.setAttribute('class', 'card-badge');
    badge.setAttribute('style', 'position:absolute;top:-10px;left:-30px;padding:5px;background:blue;color:white;transform:rotate(-20deg);');
    badge.innerHTML = text;
    this.shadowRoot.appendChild(badge);
  }

  set productId(id) {
    if (id==null) {
      this.removeAttribute('productid');
    } else {
      this.setAttribute('productid', id);
    }
  }

  fetchOffer() {
    $.get({
      url: "/ajax/product/id/offer".replace('id', this.getAttribute('productid')),
      context: this,
      success: function(data) {
        if (data['found']) {
          this.stock = data['offer']['stock'];
          this.price = data['offer']['price'];
          this.supplier = data['offer']['supplier'];
          this.offerid = data['offer']['id'];
          this.disabled = false;
          if (data['text'] !== '') {
            this.badge = data['text'];
          }
        } else {
          this.stock = "-"
          this.price = "-"
          this.supplier = "-"
          this.badge = data['text'];
        }
      },
      fail: function() {
        alert("fehler");
      }
    });
  }

  renderDom() {
    this.setAttribute('class', 'card mb-3');
    this.setAttribute('disabled', "");
    var shadow = this.attachShadow({mode: 'open'});
    var rowDiv = document.createElement('div');
    rowDiv.setAttribute('class','row no-gutters');

    var imageContainer = document.createElement('div');
    imageContainer.setAttribute('class', 'col-md-4');
    rowDiv.appendChild(imageContainer);

    var image = document.createElement('img');
    image.setAttribute('class','card-img');
    image.setAttribute('alt', '...');
    image.setAttribute('src', this.getAttribute('image'));
    imageContainer.appendChild(image);

    var body = document.createElement('div');
    body.setAttribute('class', 'col-md-8');
    rowDiv.appendChild(body);

    var cardBody = document.createElement('div');
    cardBody.setAttribute('class', 'card-body');
    cardBody.setAttribute('style', 'padding: 1rem;');
    body.appendChild(cardBody);

    var cardTitle = document.createElement('h5');
    cardTitle.setAttribute('class', 'card-title');
    cardTitle.setAttribute('id', 'title');
    cardTitle.innerHTML = this.getAttribute('description');
    cardBody.appendChild(cardTitle);

    // Information grid
    var cardText = document.createElement('div');
    cardText.setAttribute('class', 'card-text row');

    var cardLeft = document.createElement('div');
    cardLeft.setAttribute('class', 'col-md-5');
    cardLeft.setAttribute('style', 'padding-right:0px;');

    var priceIcon = document.createElement('i');
    priceIcon.setAttribute('class', 'fas fa-money-bill-wave');

    var price = document.createElement('span');
    price.setAttribute('id', 'price');
    price.innerHTML = " <span class='fas fa-sync fa-spin' role='status' aria-hidden='true'></span>";

    var stockIcon = document.createElement('i');
    stockIcon.setAttribute('class', 'fas fa-boxes');

    var stock = document.createElement('span');
    stock.setAttribute('id', 'stock');
    stock.innerHTML = " <span class='fas fa-sync fa-spin' role='status' aria-hidden='true'></span>";

    cardLeft.appendChild(priceIcon);
    cardLeft.appendChild(price);
    cardLeft.appendChild(document.createElement('br'));
    cardLeft.appendChild(stockIcon);
    cardLeft.appendChild(stock);

    var cardRight = document.createElement('div');
    cardRight.setAttribute('class', 'col-md-7');

    var supplierIcon = document.createElement('i');
    supplierIcon.setAttribute('class', 'fas fa-people-carry');

    var supplier = document.createElement('div');
    supplier.setAttribute('style', 'max-width: 110px;padding-right:0px;');
    supplier.setAttribute('id', 'supplier');
    supplier.setAttribute('class', 'text-truncate');
    supplier.appendChild(supplierIcon);
    supplier.innerHTML = supplier.innerHTML + " <span class='fas fa-sync fa-spin' role='status' aria-hidden='true'></span>";
    //cardRight.appendChild(supplierIcon);
    cardRight.appendChild(supplier);

    cardText.appendChild(cardLeft);
    cardText.appendChild(cardRight);

    shadow.innerHTML = '<style>.card .card-badge {position:absolute;top:-10px;left:-30px;padding:5px;background:blue;color:white;transform:rotate(-20deg);}</style><link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css" integrity="sha384-GJzZqFGwb1QTTN6wy59ffF1BuGJpLSa9DkKMp0DgiMDm4iYMj70gZWKYbI706tWS" crossorigin="anonymous"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.11.2/css/all.css">'
    cardBody.appendChild(cardText);
    shadow.appendChild(rowDiv);
    return
  }
}

customElements.define('product-card', ProductCard);
