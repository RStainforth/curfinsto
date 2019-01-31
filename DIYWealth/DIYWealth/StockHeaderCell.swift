//
//  StockHeaderCell.swift
//  DIYWealth
//
//  Created by John Walker on 25/01/2019.
//  Copyright © 2019 DIYWealth. All rights reserved.
//

import UIKit

class StockHeaderCell: UITableViewCell {
    
    @IBOutlet weak var headerLabel: UILabel!
    @IBOutlet weak var headerText: UITextView!
    
    override func awakeFromNib() {
        super.awakeFromNib()
        // Initialization code
    }

    override func setSelected(_ selected: Bool, animated: Bool) {
        super.setSelected(selected, animated: animated)

        // Configure the view for the selected state
    }

}
